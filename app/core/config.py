"""
Application configuration settings
"""
import os
from typing import List

from pydantic_settings import BaseSettings


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
        super().__init__(**kwargs)
        # Convert postgres:// to postgresql+asyncpg:// for async support
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = convert_postgres_url(self.DATABASE_URL)
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
