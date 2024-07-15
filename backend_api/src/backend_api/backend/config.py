from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BACKEND_API_", case_sensitive=False)

    jwt_secret_key: str = Field(validation_alias="BACKEND_API_JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_in: int = 1440

    database_url: str = Field(validation_alias="BACKEND_API_DATABASE_URL")
    provider_api_url: str = Field(validation_alias="BACKEND_API_PROVIDER_API_URL")    


settings = Settings()  # type: ignore


@lru_cache
def get_settings() -> Settings:
    return settings
