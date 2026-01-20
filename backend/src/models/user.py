"""
User models for authentication and profiles.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class UserRole(str, Enum):
    """Available user roles in the OSF network."""
    INVESTOR = "investor"
    RENTER = "renter"
    TENANT = "tenant"
    HOMEOWNER = "homeowner"
    CUSTODIAN = "custodian"  # Service Provider
    FOUNDATION = "foundation"


class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    display_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation request."""
    pass


class UserInDB(UserBase):
    """User as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    google_id: Optional[str] = None
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.INVESTOR])
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Simulation state
    balance: float = 100000.0
    network_month: int = 0
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response (public fields only)."""
    id: str
    email: str
    display_name: Optional[str]
    roles: List[UserRole]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update request."""
    display_name: Optional[str] = None
    roles: Optional[List[UserRole]] = None


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class AuthRequest(BaseModel):
    """Dev/test auth request."""
    email: EmailStr
    display_name: Optional[str] = None


class GoogleCallbackRequest(BaseModel):
    """Google OAuth callback request."""
    code: str
    state: Optional[str] = None


# In-memory user store for demo (replace with database in production)
# This allows the simulation to work without a database connection
_users_store: dict[str, UserInDB] = {}


def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user by email from in-memory store."""
    for user in _users_store.values():
        if user.email == email:
            return user
    return None


def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """Get user by ID from in-memory store."""
    return _users_store.get(user_id)


def get_user_by_google_id(google_id: str) -> Optional[UserInDB]:
    """Get user by Google ID from in-memory store."""
    for user in _users_store.values():
        if user.google_id == google_id:
            return user
    return None


def create_user(email: str, display_name: Optional[str] = None, google_id: Optional[str] = None) -> UserInDB:
    """Create a new user in the in-memory store."""
    user = UserInDB(
        email=email,
        display_name=display_name or email.split("@")[0],
        google_id=google_id,
    )
    _users_store[user.id] = user
    return user


def update_user(user_id: str, updates: UserUpdate) -> Optional[UserInDB]:
    """Update a user in the in-memory store."""
    user = _users_store.get(user_id)
    if not user:
        return None
    
    if updates.display_name is not None:
        user.display_name = updates.display_name
    if updates.roles is not None:
        user.roles = updates.roles
    user.updated_at = datetime.utcnow()
    
    return user


def get_or_create_user(email: str, display_name: Optional[str] = None, google_id: Optional[str] = None) -> UserInDB:
    """Get existing user or create new one."""
    # Try to find by Google ID first
    if google_id:
        user = get_user_by_google_id(google_id)
        if user:
            return user
    
    # Try to find by email
    user = get_user_by_email(email)
    if user:
        # Update Google ID if provided
        if google_id and not user.google_id:
            user.google_id = google_id
            user.updated_at = datetime.utcnow()
        return user
    
    # Create new user
    return create_user(email, display_name, google_id)
