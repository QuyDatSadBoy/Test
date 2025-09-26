import uuid
from typing import Optional

# from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "MultiAgent API"
    DATABASE_URL: str
    DEBUG: bool = False

    # postgres_db: str
    # postgres_user: str
    # postgres_password: str
    # postgres_host: str
    # postgres_port: int

    # MinIO settings
    # minio_root_user: str
    # minio_root_password: str
    # minio_endpoint: str

    # Kibana settings
    # kibana_public_baseurl: str

    # Auth settings
    AUTH_ENABLED: bool = False  # Set to False to disable auth in development
    # CHANGE THIS: The type hint should be uuid.UUID
    MOCK_USER_ID: Optional[uuid.UUID] = uuid.UUID(
        "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    )  # <-- Wrap the string in uuid.UUID()
    MOCK_USER_ROLE: Optional[str] = "admin"  # This can remain a string

    # LiteLLM Configuration
    LITELLM_MODEL: str = "gpt-4o-mlops5"
    LITELLM_BASE_URL: str = "http://localhost:4000"
    LITELLM_API_KEY: Optional[str] = None
    LITELLM_TEMPERATURE: float = 0.7
    LITELLM_MAX_TOKENS: int = 4000

    # Langfuse Configuration
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "http://localhost:3000"
    LANGFUSE_ENABLED: bool = False
    LITELLM_MODEL_PROVIDER: str = "openai"

    # Database URLs for different services
    POSTGRES_URL: str = "postgresql://postgres:admin@localhost:5432/postgres"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    QDRANT_URL: str = "http://localhost:6333"
    MINIO_URL: str = "http://localhost:9000"
    REDIS_URL: str = "redis://:admin@localhost:6379/0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
