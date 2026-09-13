from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StayMatch Recommendation Service"

settings = Settings()
