import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StayMatch Search Microservice"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "staymatch_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "staymatch_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "staymatch_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    EMBEDDING_BACKEND: str = os.getenv("EMBEDDING_BACKEND", "sentence-transformers")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_INDEX_DIR: str = os.getenv("VECTOR_INDEX_DIR", "")
    INDEX_REFRESH_INTERVAL_SECONDS: float = float(os.getenv("INDEX_REFRESH_INTERVAL_SECONDS", "60"))
    SEARCH_ADMIN_TOKEN: str = os.getenv("SEARCH_ADMIN_TOKEN", "")
    # Shared with the core API (its Django SECRET_KEY) so chat can verify the access tokens it issues.
    JWT_SIGNING_KEY: str = os.getenv("JWT_SIGNING_KEY", "")
    CORS_ALLOWED_ORIGINS: str = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost,http://localhost:3000,http://localhost:8000,http://localhost:5173",
    )

    def allowed_origins(self):
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
