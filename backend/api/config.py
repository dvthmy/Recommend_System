from typing import List, Union
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ===== App Info =====
    APP_NAME: str = "Food Recommendation API"
    API_VERSION: str = "1.0.0"

    # ===== Neo4j Configuration =====
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "Admin123!"
    NEO4J_DATABASE: str = "test"

    # ===== CORS =====
    # Supports list or comma-separated string
    CORS_ALLOW_ORIGINS: Union[List[str], str] = "*"  # Allow all origins for development

    # ===== JWT Configuration =====
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production-use-env-variable"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
