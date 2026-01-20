"""
Authentication module for OSF Demo.

Supports three modes:
- dev: Any email works, no verification (local development)
- test: Predefined test accounts (CI/CD, automated testing)
- google: Full Google OAuth (production)

Set AUTH_MODE environment variable to switch modes.
"""

from .config import AuthSettings, AuthMode, get_auth_settings
from .router import router as auth_router
from .dependencies import get_current_user, get_optional_user

__all__ = [
    "AuthSettings",
    "AuthMode", 
    "get_auth_settings",
    "auth_router",
    "get_current_user",
    "get_optional_user",
]
