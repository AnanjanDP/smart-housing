import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

settings = Settings()
