import logging
import re
import secrets

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.cookies import clear_refresh_cookie, read_refresh_cookie, set_refresh_cookie
from apps.users.models import User
from apps.users.oauth import (
    OAuthVerificationError,
    VerifiedIdentity,
    demo_login_enabled,
    verify_supabase_token,
)
from apps.users.serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)


class AuthThrottleMixin:
    """Sign-in, sign-up and OAuth endpoints share a tighter rate limit than the rest of the API."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


class CustomTokenObtainPairView(AuthThrottleMixin, TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop('refresh', None) if response.status_code == 200 else None
        if refresh:
            set_refresh_cookie(response, refresh)
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Issues a new access token (and rotates the refresh token) from the refresh cookie."""

    def post(self, request, *args, **kwargs):
        refresh = read_refresh_cookie(request)
        if not refresh:
            return Response({'detail': 'Not signed in.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data={'refresh': refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, InvalidToken):
            return clear_refresh_cookie(
                Response({'detail': 'Session expired.'}, status=status.HTTP_401_UNAUTHORIZED))
        data = dict(serializer.validated_data)
        new_refresh = data.pop('refresh', None)
        response = Response(data, status=status.HTTP_200_OK)
        if new_refresh:
            set_refresh_cookie(response, new_refresh)
        return response

class LogoutView(APIView):
    """Ends a session by blacklisting its refresh token, so it can't be used to mint new access tokens."""
    permission_classes = [permissions.AllowAny]  # an expired access token must not stop someone logging out
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request):
        refresh = read_refresh_cookie(request)
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass  # already expired or blacklisted: the goal (token unusable) is met
        return clear_refresh_cookie(Response(status=status.HTTP_204_NO_CONTENT))


class RegisterView(AuthThrottleMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


def _unique_username(email: str) -> str:
    base = re.sub(r'[^\w.@+-]', '', email.split('@')[0])[:30] or 'user'
    candidate = base
    while User.objects.filter(username__iexact=candidate).exists():
        candidate = f"{base}-{secrets.token_hex(2)}"
    return candidate


def _split_name(name: str):
    parts = name.split() if name else []
    return (parts[0] if parts else ''), (' '.join(parts[1:]) if len(parts) > 1 else '')


class OAuthOIDCLoginView(AuthThrottleMixin, APIView):
    """Sign in with an identity token issued by the OAuth provider (Supabase).

    The token's signature, expiry, audience and issuer are verified on the server, and the email
    address is taken only from the verified token. Nothing the client sends alongside the token is
    trusted. The typed-email shortcut used by the local demo form only works when
    ALLOW_INSECURE_DEMO_OAUTH is set and DEBUG is on, and it can never sign in to an account that
    has a password.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('id_token') or request.data.get('access_token')
        requested_role = request.data.get('role', User.Role.TENANT)
        demo = False

        if token:
            try:
                identity = verify_supabase_token(token)
            except OAuthVerificationError as exc:
                logger.warning("Rejected OAuth login: %s", exc)
                return Response({'detail': 'Invalid or unverifiable identity token.'}, status=status.HTTP_401_UNAUTHORIZED)
            if not identity.email or not identity.email_verified:
                return Response({'detail': 'A verified email address is required.'}, status=status.HTTP_401_UNAUTHORIZED)
        elif demo_login_enabled():
            email = str(request.data.get('email') or '').strip().lower()
            try:
                validate_email(email)
            except DjangoValidationError:
                return Response({'detail': 'A valid email is required.'}, status=status.HTTP_400_BAD_REQUEST)
            identity = VerifiedIdentity(
                subject=str(request.data.get('sub') or ''),
                email=email,
                email_verified=True,
                name=str(request.data.get('name') or '').strip(),
                avatar_url=request.data.get('avatar_url'),
                provider='demo',
            )
            demo = True
        else:
            return Response({'detail': 'A verified identity token is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(email__iexact=identity.email).first()
        first_name, last_name = _split_name(identity.name)

        if user is None:
            role = requested_role if requested_role in (User.Role.TENANT, User.Role.LANDLORD) else User.Role.TENANT
            user = User.objects.create_user(
                email=identity.email,
                username=_unique_username(identity.email),
                password=None,
                first_name=first_name,
                last_name=last_name,
                role=role,
                avatar_url=identity.avatar_url or '',
            )
        else:
            if demo and user.has_usable_password():
                return Response(
                    {'detail': 'Demo sign-in cannot be used for accounts that have a password.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not user.is_active:
                return Response({'detail': 'This account is disabled.'}, status=status.HTTP_403_FORBIDDEN)
            changed = False
            if first_name and not user.first_name:
                user.first_name, user.last_name, changed = first_name, last_name, True
            if identity.avatar_url and not user.avatar_url:
                user.avatar_url, changed = identity.avatar_url, True
            if changed:
                user.save()

        refresh = RefreshToken.for_user(user)
        response = Response({
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        return set_refresh_cookie(response, refresh)
