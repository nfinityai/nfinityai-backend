import logging
from http import HTTPStatus

import aiohttp
from fastapi import Depends
from typing_extensions import Annotated

from backend_api.backend.config import Settings, get_settings

logger = logging.getLogger(__name__)


class ModelProviderException(Exception):
    pass


class ModelProviderService:
    def __init__(self, settings: Settings) -> None:
        self.api_url = settings.provider_api_url
        self.session = aiohttp.ClientSession()

    async def list_categories(self):
        async with self.session.get(
            self.api_url + "/replicate/collections"
        ) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing categories: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()

    async def list_models(self, category: str):
        async with self.session.get(
            self.api_url + f"/replicate/collections/{category}/models"
        ) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()

    async def run_model(self, model: str, params: dict):
        async with self.session.post(
            self.api_url + f"/replicate/run/{model}", json=params
        ) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()


def get_model_provider_service(settings: Annotated[Settings, Depends(get_settings)]):
    return ModelProviderService(settings)
