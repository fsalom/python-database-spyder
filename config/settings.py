"""Application settings using Pydantic Settings."""

from typing import Literal, Optional
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    driver: Literal["postgresql", "mysql", "sqlite"] = "postgresql"
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "postgres"
    database: str = "spyder_metadata"

    # SQLAlchemy settings
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10

    @property
    def url(self) -> str:
        """Generate database URL."""
        if self.driver == "sqlite":
            return f"sqlite+aiosqlite:///./{self.database}.db"
        elif self.driver == "postgresql":
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.driver == "mysql":
            return f"mysql+aiomysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        raise ValueError(f"Unsupported database driver: {self.driver}")

    @property
    def sync_url(self) -> str:
        """Generate synchronous database URL (for Alembic)."""
        if self.driver == "sqlite":
            return f"sqlite:///./{self.database}.db"
        elif self.driver == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.driver == "mysql":
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        raise ValueError(f"Unsupported database driver: {self.driver}")


class AdminPanelSettings(BaseSettings):
    """Admin panel (full-stack-fastapi-template) connection settings."""

    enabled: bool = True
    base_url: str = "http://localhost:8001"
    api_key: Optional[str] = None
    sync_enabled: bool = True  # Auto-sync entities to admin panel


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    # Application
    app_name: str = "Spyder - Dynamic API Generator"
    version: str = "1.0.0"
    debug: bool = Field(default=False, validation_alias="DEBUG")

    # API
    api_v1_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["*"]

    # Security
    secret_key: str = Field(
        default="change-me-in-production-please-use-a-secure-random-key",
        min_length=32
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Admin Panel
    admin_panel: AdminPanelSettings = Field(default_factory=AdminPanelSettings)

    # Celery (for background tasks)
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"


# Global settings instance
settings = Settings()
