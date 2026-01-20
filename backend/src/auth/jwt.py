"""
JWT token utilities for authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from pydantic import BaseModel

from .config import get_auth_settings


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    email: str
    exp: datetime
    iat: datetime
    type: str = "access"


class TokenError(Exception):
    """Token validation error."""
    pass


def create_access_token(user_id: str, email: str) -> tuple[str, int]:
    """
    Create a JWT access token.
    
    Returns:
        Tuple of (token_string, expires_in_seconds)
    """
    settings = get_auth_settings()
    
    now = datetime.utcnow()
    expires_delta = timedelta(hours=settings.jwt_expiry_hours)
    expires_at = now + expires_delta
    
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }
    
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    expires_in = int(expires_delta.total_seconds())
    
    return token, expires_in


def decode_access_token(token: str) -> TokenPayload:
    """
    Decode and validate a JWT access token.
    
    Raises:
        TokenError: If token is invalid or expired
    """
    settings = get_auth_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        
        return TokenPayload(
            sub=payload["sub"],
            email=payload["email"],
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"]),
            type=payload.get("type", "access"),
        )
        
    except JWTError as e:
        if "expired" in str(e).lower():
            raise TokenError("Token has expired")
        raise TokenError(f"Invalid token: {str(e)}")


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Expects format: "Bearer <token>"
    """
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]
