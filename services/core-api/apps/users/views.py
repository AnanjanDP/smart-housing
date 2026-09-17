from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.users.serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class OAuthOIDCLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get('id_token')
        email = request.data.get('email')
        name = request.data.get('name', '').strip()
        provider = request.data.get('provider', 'google_oidc')
        avatar_url = request.data.get('avatar_url')
        requested_role = request.data.get('role', User.Role.TENANT)

        # Handle raw OIDC payload if id_token is provided
        if id_token and not email:
            import base64
            import json
            try:
                # Basic JWT header.payload.signature split decoding for OIDC token payload
                parts = id_token.split('.')
                if len(parts) >= 2:
                    padding = '=' * (4 - len(parts[1]) % 4)
                    payload_bytes = base64.b64decode(parts[1] + padding)
                    claims = json.loads(payload_bytes)
                    email = claims.get('email', email)
                    name = claims.get('name', name)
                    avatar_url = claims.get('picture', avatar_url)
            except Exception:
                pass

        if not email:
            email = f"oauth_user_{request.data.get('sub', 'demo')}@staymatch.com"
            name = name or "OAuth User"

        name_parts = name.split() if name else []
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        username = email.split('@')[0]
        user = User.objects.filter(email=email).first() or User.objects.filter(username=username).first()
        
        valid_role = requested_role if requested_role in [User.Role.TENANT, User.Role.LANDLORD] else User.Role.TENANT

        if not user:
            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=valid_role,
                avatar_url=avatar_url,
                password=User.objects.make_random_password()
            )
        else:
            if first_name or last_name:
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
            if avatar_url:
                user.avatar_url = avatar_url
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

