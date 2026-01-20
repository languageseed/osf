"""
Authentication API routes.

Supports three modes:
- dev: Any email works (local development)
- test: Predefined test accounts (CI/CD)
- google: Full Google OAuth (production)
"""

from typing import Optional
import httpx
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse

from .config import get_auth_settings, AuthMode, TEST_USERS
from .jwt import create_access_token
from .dependencies import get_current_user
from ..models.user import (
    UserInDB,
    UserResponse,
    TokenResponse,
    AuthRequest,
    UserUpdate,
    UserRole,
    get_or_create_user,
    get_user_by_id,
    update_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/config")
async def get_auth_config():
    """
    Get current auth configuration.
    
    Returns the auth mode so frontend knows which login method to show.
    """
    settings = get_auth_settings()
    
    return {
        "mode": settings.auth_mode.value,
        "google_client_id": settings.google_client_id if settings.auth_mode == AuthMode.GOOGLE else None,
        "google_enabled": settings.auth_mode == AuthMode.GOOGLE and bool(settings.google_client_id),
    }


# =============================================================================
# DEV MODE: Simple email login (no verification)
# =============================================================================

@router.post("/dev/login", response_model=TokenResponse)
async def dev_login(request: AuthRequest):
    """
    Dev mode: Login with just an email.
    
    No verification required. Any email address works.
    Only available when AUTH_MODE=dev.
    """
    settings = get_auth_settings()
    
    if settings.auth_mode != AuthMode.DEV:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Dev login not available in {settings.auth_mode.value} mode"
        )
    
    # Get or create user
    user = get_or_create_user(
        email=request.email,
        display_name=request.display_name
    )
    
    # Create token
    token, expires_in = create_access_token(user.id, user.email)
    
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


# =============================================================================
# TEST MODE: Predefined test accounts
# =============================================================================

@router.get("/test/users")
async def list_test_users():
    """
    List available test users.
    
    Only available when AUTH_MODE=test.
    """
    settings = get_auth_settings()
    
    if settings.auth_mode != AuthMode.TEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Test users not available in {settings.auth_mode.value} mode"
        )
    
    return {"users": TEST_USERS}


@router.post("/test/login", response_model=TokenResponse)
async def test_login(user_id: str = Query(..., description="Test user ID")):
    """
    Test mode: Login as a predefined test user.
    
    Only available when AUTH_MODE=test.
    """
    settings = get_auth_settings()
    
    if settings.auth_mode != AuthMode.TEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Test login not available in {settings.auth_mode.value} mode"
        )
    
    # Find test user
    test_user = next((u for u in TEST_USERS if u["id"] == user_id), None)
    if not test_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test user '{user_id}' not found"
        )
    
    # Create user object
    user = UserInDB(
        id=test_user["id"],
        email=test_user["email"],
        display_name=test_user["display_name"],
        roles=[UserRole(r) for r in test_user["roles"]],
    )
    
    # Create token
    token, expires_in = create_access_token(user.id, user.email)
    
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


# =============================================================================
# GOOGLE OAUTH MODE: Full OAuth flow
# =============================================================================

@router.get("/google/login")
async def google_login(redirect_uri: Optional[str] = None):
    """
    Initiate Google OAuth flow.
    
    Redirects to Google's OAuth consent screen.
    Only available when AUTH_MODE=google.
    """
    settings = get_auth_settings()
    
    if settings.auth_mode != AuthMode.GOOGLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Google login not available in {settings.auth_mode.value} mode"
        )
    
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    # Use provided redirect URI or default
    callback_uri = redirect_uri or settings.google_redirect_uri
    
    # Build Google OAuth URL
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={callback_uri}&"
        "response_type=code&"
        "scope=email profile&"
        "access_type=offline&"
        "prompt=consent"
    )
    
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    error: Optional[str] = Query(None, description="Error from Google"),
):
    """
    Handle Google OAuth callback.
    
    Exchanges authorization code for tokens and creates/updates user.
    """
    settings = get_auth_settings()
    
    if settings.auth_mode != AuthMode.GOOGLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Google callback not available in {settings.auth_mode.value} mode"
        )
    
    if error:
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{settings.frontend_url}/auth/login?error={error}"
        )
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code"
                )
            
            tokens = token_response.json()
            access_token = tokens["access_token"]
            
            # Get user info from Google
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google"
                )
            
            userinfo = userinfo_response.json()
        
        # Create or update user
        user = get_or_create_user(
            email=userinfo["email"],
            display_name=userinfo.get("name"),
            google_id=userinfo["id"]
        )
        
        # Create our JWT token
        jwt_token, expires_in = create_access_token(user.id, user.email)
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.frontend_url}/auth/callback?token={jwt_token}"
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth error: {str(e)}"
        )


# =============================================================================
# COMMON ENDPOINTS (All modes)
# =============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: UserInDB = Depends(get_current_user)):
    """
    Get current authenticated user's info.
    """
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    updates: UserUpdate,
    user: UserInDB = Depends(get_current_user)
):
    """
    Update current user's profile.
    """
    updated_user = update_user(user.id, updates)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(updated_user)


@router.post("/me/roles/{role}")
async def add_role(
    role: UserRole,
    user: UserInDB = Depends(get_current_user)
):
    """
    Add a role to current user.
    """
    if role not in user.roles:
        user.roles.append(role)
    return {"roles": user.roles}


@router.delete("/me/roles/{role}")
async def remove_role(
    role: UserRole,
    user: UserInDB = Depends(get_current_user)
):
    """
    Remove a role from current user.
    """
    if role in user.roles:
        user.roles.remove(role)
    return {"roles": user.roles}


@router.post("/logout")
async def logout():
    """
    Logout current user.
    
    Note: JWT tokens are stateless, so this just returns success.
    The frontend should delete the stored token.
    """
    return {"message": "Logged out successfully"}
