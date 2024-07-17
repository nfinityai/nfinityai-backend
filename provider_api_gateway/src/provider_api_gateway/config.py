from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    replicate_api_token: str

    replicate_hardware_pricing_url: str = 'https://replicate.com/pricing'

@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
