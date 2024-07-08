from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROVIDER_REPLICATE_API_KEY: str
    PROVIDER_REPLICATE_RETRY_ATTEMPTS: int = 3

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
