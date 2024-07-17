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
    provider_api_retry_attempts: int = Field(default=3, validation_alias="BACKEND_API_PROVIDER_API_RETRY_ATTEMPTS")
    provider_api_factor: int = Field(default=2, validation_alias="BACKEND_API_PROVIDER_API_RETRY_FACTOR")

    provider: str = Field(validation_alias="BACKEND_API_PROVIDER_NAME")


    free_trial_mode: bool = Field(default=True, validation_alias="BACKEND_API_FREE_TRIAL_MODE")
    free_trial_credits: int = Field(default=500, validation_alias="BACKEND_API_FREE_TRIAL_CREDITS")



@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
