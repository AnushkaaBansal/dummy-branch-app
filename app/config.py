"""Application configuration settings.

This module defines the configuration settings for the application using Pydantic's
BaseSettings. It supports different environments (development, testing, production)
and loads configuration from environment variables with sensible defaults.
"""
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    validator,
    Field,
)

# Project root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# Environment detection
ENV = os.getenv("ENV", "development").lower()
IS_TESTING = "pytest" in sys.modules or "test" in sys.argv


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Branch Loans API"
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
        min_length=32,
    )
    API_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    # Database
    DATABASE_URI: Optional[PostgresDsn] = None
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "microloans")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Database connection pool settings
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    DATABASE_POOL_PRE_PING: bool = os.getenv("DATABASE_POOL_PRE_PING", "true").lower() == "true"
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
    
    # SQLAlchemy settings
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"
    SQL_ECHO_POOL: bool = os.getenv("SQL_ECHO_POOL", "false").lower() == "true"
    
    # Security
    SECURITY_PASSWORD_SALT: str = os.getenv(
        "SECURITY_PASSWORD_SALT", "dev-salt-change-in-production"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    JSON_LOGS: bool = os.getenv("JSON_LOGS", "false").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Email
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    SMTP_SSL: bool = os.getenv("SMTP_SSL", "false").lower() == "true"
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME")
    
    # First superuser
    FIRST_SUPERUSER: EmailStr = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "changethis")
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # Rate limiting
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "100/minute")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Union[str, PostgresDsn]:
        if isinstance(v, str):
            return v
        
        # For testing, use SQLite
        if values.get("TESTING"):
            return "sqlite:///./test.db"
        
        # Build PostgreSQL DSN
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f'/{values.get("POSTGRES_DB") or ""}',
        )
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("[") and v != "*":
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins_list(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("[") and v != "*":
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v if isinstance(v, list) else [v]
        raise ValueError(v)
    
    @property
    def DATABASE_URL(self) -> str:
        """Get the database URL."""
        if self.DATABASE_URI:
            return str(self.DATABASE_URI)
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg2",
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=f'/{self.POSTGRES_DB or ""}',
            )
        )


class DevelopmentConfig(Settings):
    """Development configuration."""
    
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    SQL_ECHO: bool = True
    
    class Config:
        env_file = ".env.development"


class TestingConfig(Settings):
    """Testing configuration."""
    
    TESTING: bool = True
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URI: str = "sqlite:///./test.db"
    
    class Config:
        env_file = ".env.test"


class ProductionConfig(Settings):
    """Production configuration."""
    
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True
    
    class Config:
        env_file = ".env.production"


# Determine which config to use based on environment
@lru_cache()
def get_settings() -> Settings:
    """Get the appropriate settings class based on the current environment."""
    env = ENV.lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing" or IS_TESTING:
        return TestingConfig()
    return DevelopmentConfig()


# Global settings instance
settings = get_settings()

# For backward compatibility
DATABASE_URL = settings.DATABASE_URL
