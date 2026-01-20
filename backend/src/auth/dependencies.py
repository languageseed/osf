"""
FastAPI dependencies for authentication.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt import decode_access_token, TokenError
from .config import get_auth_settings, AuthMode, TEST_USERS
from ..models.user import UserInDB, get_user_by_id, UserRole

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserInDB:
    """
    Get the current authenticated user.
    
    Raises HTTPException 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if it's a test user
    settings = get_auth_settings()
    if settings.auth_mode == AuthMode.TEST:
        test_user = next((u for u in TEST_USERS if u["id"] == payload.sub), None)
        if test_user:
            return UserInDB(
                id=test_user["id"],
                email=test_user["email"],
                display_name=test_user["display_name"],
                roles=[UserRole(r) for r in test_user["roles"]],
            )
    
    # Get user from store
    user = get_user_by_id(payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserInDB]:
    """
    Get the current user if authenticated, None otherwise.
    
    Does not raise an exception if not authenticated.
    """
    if not credentials:
        return None
    
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError:
        return None
    
    # Check if it's a test user
    settings = get_auth_settings()
    if settings.auth_mode == AuthMode.TEST:
        test_user = next((u for u in TEST_USERS if u["id"] == payload.sub), None)
        if test_user:
            return UserInDB(
                id=test_user["id"],
                email=test_user["email"],
                display_name=test_user["display_name"],
                roles=[UserRole(r) for r in test_user["roles"]],
            )
    
    return get_user_by_id(payload.sub)


def require_role(required_role: UserRole):
    """
    Dependency factory to require a specific role.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: UserInDB = Depends(require_role(UserRole.FOUNDATION))):
            ...
    """
    async def role_checker(user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if required_role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' required",
            )
        return user
    
    return role_checker


def require_any_role(*required_roles: UserRole):
    """
    Dependency factory to require any of the specified roles.
    
    Usage:
        @router.get("/property")
        async def property_endpoint(
            user: UserInDB = Depends(require_any_role(UserRole.HOMEOWNER, UserRole.CUSTODIAN))
        ):
            ...
    """
    async def role_checker(user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if not any(role in user.roles for role in required_roles):
            role_names = ", ".join(r.value for r in required_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {role_names}",
            )
        return user
    
    return role_checker
