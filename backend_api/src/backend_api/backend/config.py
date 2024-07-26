from functools import lru_cache
import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


@lru_cache
def _get_contract_abi():
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data/contract_abi.json"
        )
    ) as f:
        return json.load(f)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BACKEND_API_", case_sensitive=False)

    secret_key: str = Field(validation_alias="BACKEND_API_SECRET_KEY")

    jwt_secret_key: str = Field(validation_alias="BACKEND_API_JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_in: int = 1440

    database_url: str = Field(validation_alias="BACKEND_API_DATABASE_URL")
    provider_api_url: str = Field(validation_alias="BACKEND_API_PROVIDER_API_URL")
    provider_api_retry_attempts: int = Field(
        default=3, validation_alias="BACKEND_API_PROVIDER_API_RETRY_ATTEMPTS"
    )
    provider_api_factor: int = Field(
        default=2, validation_alias="BACKEND_API_PROVIDER_API_RETRY_FACTOR"
    )

    provider: str = Field(validation_alias="BACKEND_API_PROVIDER_NAME")

    free_trial_mode: bool = Field(
        default=True, validation_alias="BACKEND_API_FREE_TRIAL_MODE"
    )
    free_trial_credits: int = Field(
        default=5, validation_alias="BACKEND_API_FREE_TRIAL_CREDITS"
    )

    default_model_cost: float = Field(
        default=2, validation_alias="BACKEND_API_DEFAULT_MODEL_COST"
    )

    admin_username: str = Field(validation_alias="BACKEND_API_ADMIN_USERNAME")
    admin_password: str = Field(validation_alias="BACKEND_API_ADMIN_PASSWORD")

    contract_address: str = Field(validation_alias="BACKEND_API_CONTRACT_ADDRESS")
    contract_abi: list = Field(default_factory=_get_contract_abi)

    infura_base_url: str = Field(validation_alias="BACKEND_API_INFURA_BASE_URL")
    coingecko_api_key: str = Field(validation_alias="BACKEND_API_COINGECKO_API_KEY")

    time_to_pay_minutes: int = Field(
        default=15, validation_alias="BACKEND_API_TIME_TO_PAY_MINUTES"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
