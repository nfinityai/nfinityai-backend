import logging
from http import HTTPStatus
from urllib.parse import urlencode, urljoin

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

    def _build_url(self, path: str, **params) -> str:
        if params:
            path = f"{path}?{urlencode(params)}"
        return urljoin(self.api_url, path)

    async def list_categories(self):
        url = self._build_url("/categories")
        async with self.session.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing categories: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()

    async def list_models(self, provider: str, category: str):
        url = self._build_url(f"/providers/{provider}/categories/{category}/models")
        async with self.session.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing models")
            return await response.json()

    async def run_model(self, provider: str, model: str, params: dict, version: str | None = None):
        url = self._build_url(f"/providers/{provider}/models/{model}/run", version=version)
        async with self.session.post(url, json={'input': params}) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()

    async def run_model_async(self, provider: str, model: str, params: dict, version: str | None = None):
        url = self._build_url(f"/providers/{provider}/models/{model}/run_async", version=version)
        async with self.session.post(url, json={'input': params}) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()


def get_model_provider_service(settings: Annotated[Settings, Depends(get_settings)]):
    return ModelProviderService(settings)
