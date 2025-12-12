from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ===== App Info =====
    APP_NAME: str = "Food Recommendation API"
    API_VERSION: str = "1.0.0"

    # ===== Neo4j Configuration =====
    # Default to Neo4j Aura - can be overridden via .env file
    NEO4J_URI: str = "neo4j+s://3b0d8961.databases.neo4j.io"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "qV5l-Ck8vasO5qoM65gjWhuJTa2HBr4e6KwSYJ0RfT0"
    NEO4J_DATABASE: str = "neo4j"

    # ===== CORS =====
    # Supports list or comma-separated string
    CORS_ALLOW_ORIGINS: Union[List[str], str] = "*"  # Allow all origins for development

    # ===== JWT Configuration =====
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production-use-env-variable"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ===== Gemini API Configuration =====
    GEMINI_API_KEY: str = ""  # Set via .env file or environment variable

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env that don't match model fields
    )


settings = Settings()
