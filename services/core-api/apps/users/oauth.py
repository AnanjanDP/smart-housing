import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import jwt
from django.conf import settings

logger = logging.getLogger(__name__)

SUPABASE_AUDIENCE = "authenticated"
JWKS_CACHE_SECONDS = 3600


class OAuthVerificationError(Exception):
    """The identity token is missing, malformed, forged, expired or not accepted."""


@dataclass(frozen=True)
class VerifiedIdentity:
    subject: str
    email: str
    email_verified: bool
    name: str
    avatar_url: Optional[str]
    provider: str


_jwks_clients: Dict[str, "jwt.PyJWKClient"] = {}


def _jwks_client(url: str) -> "jwt.PyJWKClient":
    client = _jwks_clients.get(url)
    if client is None:
        client = jwt.PyJWKClient(url, cache_keys=True, lifespan=JWKS_CACHE_SECONDS)
        _jwks_clients[url] = client
    return client


def _signing_key_and_algorithm(token: str):
    """Choose the verification key from server configuration, never from the token itself.

    The token's header only selects between the algorithms we have configured keys for, and the
    chosen algorithm is the only one passed to the decoder. This prevents "alg: none" tokens and
    algorithm-confusion attacks (an RSA public key being used as an HMAC secret).
    """
    secret = getattr(settings, "SUPABASE_JWT_SECRET", "") or ""
    base_url = (getattr(settings, "SUPABASE_URL", "") or "").rstrip("/")

    try:
        algorithm = jwt.get_unverified_header(token).get("alg")
    except jwt.PyJWTError as exc:
        raise OAuthVerificationError("Malformed token") from exc

    if algorithm == "HS256" and secret:
        return secret, algorithm
    if algorithm in ("RS256", "ES256") and base_url:
        try:
            key = _jwks_client(f"{base_url}/auth/v1/.well-known/jwks.json").get_signing_key_from_jwt(token).key
        except Exception as exc:
            logger.warning("Could not obtain the signing key for an OAuth token: %s", exc)
            raise OAuthVerificationError("Signing key unavailable") from exc
        return key, algorithm

    raise OAuthVerificationError("Token algorithm is not accepted or token verification is not configured")


def verify_supabase_token(token: Any) -> VerifiedIdentity:
    if not isinstance(token, str) or token.count(".") != 2:
        raise OAuthVerificationError("Malformed token")

    key, algorithm = _signing_key_and_algorithm(token)
    base_url = (getattr(settings, "SUPABASE_URL", "") or "").rstrip("/")

    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            audience=SUPABASE_AUDIENCE,
            issuer=f"{base_url}/auth/v1" if base_url else None,
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise OAuthVerificationError(f"Token rejected: {exc.__class__.__name__}") from exc

    metadata = claims.get("user_metadata") or {}
    app_metadata = claims.get("app_metadata") or {}
    email = str(claims.get("email") or "").strip().lower()
    return VerifiedIdentity(
        subject=str(claims["sub"]),
        email=email,
        email_verified=metadata.get("email_verified") is True,
        name=str(metadata.get("full_name") or metadata.get("name") or "").strip(),
        avatar_url=metadata.get("avatar_url") or metadata.get("picture"),
        provider=str(app_metadata.get("provider") or "oauth"),
    )


def demo_login_enabled() -> bool:
    """The typed-email demo login exists for local development only."""
    return bool(getattr(settings, "ALLOW_INSECURE_DEMO_OAUTH", False)) and bool(settings.DEBUG)
