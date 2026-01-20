"""
Authentication configuration.

Supports flexible auth modes for dev, test, and production.
"""

from enum import Enum
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class AuthMode(str, Enum):
    """Authentication mode."""
    DEV = "dev"       # Any email works, no verification
    TEST = "test"     # Predefined test accounts only
    GOOGLE = "google" # Full Google OAuth


class AuthSettings(BaseSettings):
    """Authentication settings loaded from environment."""
    
    # Auth mode
    auth_mode: AuthMode = Field(default=AuthMode.DEV, alias="AUTH_MODE")
    
    # JWT settings
    jwt_secret: str = Field(
        default="dev-secret-change-in-production-immediately",
        alias="AUTH_JWT_SECRET"
    )
    jwt_algorithm: str = Field(default="HS256", alias="AUTH_JWT_ALGORITHM")
    jwt_expiry_hours: int = Field(default=24, alias="AUTH_JWT_EXPIRY_HOURS")
    
    # Google OAuth settings (only needed in google mode)
    google_client_id: str = Field(default="", alias="AUTH_GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="AUTH_GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:5173/auth/callback",
        alias="AUTH_GOOGLE_REDIRECT_URI"
    )
    
    # Frontend URL for redirects
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_auth_settings() -> AuthSettings:
    """Get cached auth settings."""
    return AuthSettings()


# Predefined test users for test mode
TEST_USERS = [
    {
        "id": "test-investor-001",
        "email": "investor@test.osf",
        "display_name": "Test Investor",
        "roles": ["investor"],
    },
    {
        "id": "test-renter-001",
        "email": "renter@test.osf",
        "display_name": "Test Renter",
        "roles": ["renter"],
    },
    {
        "id": "test-tenant-001",
        "email": "tenant@test.osf",
        "display_name": "Test Tenant",
        "roles": ["tenant"],
    },
    {
        "id": "test-homeowner-001",
        "email": "homeowner@test.osf",
        "display_name": "Test Homeowner",
        "roles": ["homeowner"],
    },
    {
        "id": "test-custodian-001",
        "email": "custodian@test.osf",
        "display_name": "Test Service Provider",
        "roles": ["custodian"],
    },
    {
        "id": "test-foundation-001",
        "email": "foundation@test.osf",
        "display_name": "Test Foundation Partner",
        "roles": ["foundation"],
    },
    {
        "id": "test-multi-001",
        "email": "multi@test.osf",
        "display_name": "Test Multi-Role User",
        "roles": ["investor", "homeowner", "foundation"],
    },
    {
        "id": "test-admin-001",
        "email": "admin@test.osf",
        "display_name": "Test Admin",
        "roles": ["investor", "renter", "tenant", "homeowner", "custodian", "foundation"],
    },
]
