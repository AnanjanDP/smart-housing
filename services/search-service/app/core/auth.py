import uuid

import jwt

from app.core.config import settings


class ChatAuthError(Exception):
    """The token is missing, malformed, expired, forged or not an access token."""


def verify_access_token(token) -> str:
    """Return the user id from a core-API access token, or raise ChatAuthError.

    Tokens are the HS256 JWTs issued by the core API; the signature, expiry and token type are all
    checked, and only HS256 is accepted.
    """
    key = settings.JWT_SIGNING_KEY
    if not key:
        raise ChatAuthError("Chat authentication is not configured")
    if not isinstance(token, str) or token.count(".") != 2:
        raise ChatAuthError("Malformed token")
    try:
        claims = jwt.decode(token, key, algorithms=["HS256"], options={"require": ["exp"]})
    except jwt.PyJWTError as exc:
        raise ChatAuthError(f"Token rejected: {exc.__class__.__name__}") from exc
    if claims.get("token_type") != "access":
        raise ChatAuthError("Not an access token")
    try:
        return str(uuid.UUID(str(claims.get("user_id"))))
    except ValueError as exc:
        raise ChatAuthError("Token has no valid user id") from exc
