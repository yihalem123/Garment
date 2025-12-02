"""
Application configuration settings
"""
import os
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def convert_postgres_url(url: str) -> str:
    """
    Convert postgres:// URL to postgresql+asyncpg:// format for async SQLAlchemy
    Render provides postgres:// URLs, but async SQLAlchemy needs postgresql+asyncpg://
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./garment.db"
    
    def __init__(self, **kwargs):
        # Remove ALLOWED_HOSTS from environment temporarily to prevent pydantic-settings from parsing it
        # We'll handle it manually and set ALLOWED_HOSTS_STR instead
        allowed_hosts_env = os.environ.pop("ALLOWED_HOSTS", None)
        if allowed_hosts_env and "ALLOWED_HOSTS_STR" not in kwargs and "ALLOWED_HOSTS_STR" not in os.environ:
            os.environ["ALLOWED_HOSTS_STR"] = allowed_hosts_env
        
        try:
            super().__init__(**kwargs)
        finally:
            # Don't restore ALLOWED_HOSTS - we don't want it in the environment
        
        # Convert postgres:// to postgresql+asyncpg:// for async support
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = convert_postgres_url(self.DATABASE_URL)
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - stored as string, converted to list via property
    # Accept both ALLOWED_HOSTS and ALLOWED_HOSTS_STR from environment
    ALLOWED_HOSTS_STR: str = "*"
    
    @model_validator(mode="before")
    @classmethod
    def map_allowed_hosts(cls, data):
        """Map ALLOWED_HOSTS env var to ALLOWED_HOSTS_STR"""
        if isinstance(data, dict):
            # Handle both ALLOWED_HOSTS and ALLOWED_HOSTS_STR
            if "ALLOWED_HOSTS" in data and "ALLOWED_HOSTS_STR" not in data:
                data["ALLOWED_HOSTS_STR"] = data.pop("ALLOWED_HOSTS")
        return data
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Parse ALLOWED_HOSTS from comma-separated string"""
        if self.ALLOWED_HOSTS_STR == "*":
            return ["*"]
        return [host.strip() for host in self.ALLOWED_HOSTS_STR.split(",") if host.strip()]
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Email (for notifications)
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    
    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
        env_ignore_empty=True,
    )


# Create settings instance
settings = Settings()
