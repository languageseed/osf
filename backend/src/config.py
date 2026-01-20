"""
OSPF Demo - Configuration
Loads from environment variables, compatible with Doppler
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # API Security
    api_secret_key: str = Field(default="", alias="API_SECRET_KEY")
    
    # Database
    database_url: str = Field(
        default="postgresql://ospf:ospf_dev@localhost:5432/ospf_demo",
        alias="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379",
        alias="REDIS_URL"
    )
    
    # Gemini AI - Using Gemini 2.0 models (latest available)
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    gemini_pro_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_PRO_MODEL")
    embedding_model: str = Field(default="text-embedding-004", alias="EMBEDDING_MODEL")
    
    # Application
    app_name: str = "OSPF Demo"
    app_version: str = "0.1.0"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def require_api_key(self) -> bool:
        """API key required if set and not in development."""
        return bool(self.api_secret_key) and not self.is_development

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
