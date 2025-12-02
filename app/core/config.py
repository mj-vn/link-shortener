from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "URL-Shortener"
    VERSION: str = "0.0.0-dev"
    APP_VERSION: str = "0.0.0-dev"
    DEBUG: bool = True
    TESTING: bool = False
    ENVIRONMENT: str = "staging"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/url_shortener"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/url_shortener"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"  # or "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

