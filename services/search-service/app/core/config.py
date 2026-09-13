import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StayMatch Search Microservice"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "staymatch_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "staymatch_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "staymatch_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
