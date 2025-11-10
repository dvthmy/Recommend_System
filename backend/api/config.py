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
    CORS_ALLOW_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
