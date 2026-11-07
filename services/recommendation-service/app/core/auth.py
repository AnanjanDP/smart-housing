import os
import uuid

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


def signing_key() -> str:
    return os.getenv("JWT_SIGNING_KEY", "")


def current_user_id(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    """The signed-in user's id, from a core-API access token (HS256, unexpired, access type)."""
    unauthorised = HTTPException(status_code=401, detail="Authentication required",
                                 headers={"WWW-Authenticate": "Bearer"})
    key = signing_key()
    if credentials is None or not key:
        raise unauthorised
    try:
        claims = jwt.decode(credentials.credentials, key, algorithms=["HS256"], options={"require": ["exp"]})
        if claims.get("token_type") != "access":
            raise unauthorised
        return str(uuid.UUID(str(claims.get("user_id"))))
    except (jwt.PyJWTError, ValueError):
        raise unauthorised
