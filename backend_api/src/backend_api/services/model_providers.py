import logging
from http import HTTPStatus
from urllib.parse import urlencode, urljoin

import aiohttp
import aiohttp_retry
from fastapi import Depends
from typing_extensions import Annotated

from backend_api.backend.config import Settings, get_settings
import time

from backend_api.schemas.model_providers import ModelProviderCategoryList, ModelProviderModelList

logger = logging.getLogger(__name__)


class ModelProviderException(Exception):
    pass

async def on_request_start(session, trace_config_ctx, params):
    trace_config_ctx.start = time.time()


async def on_request_end(session, trace_config_ctx, params):
    elapsed = time.time() - trace_config_ctx.start
    logger.info(f"Request to api finished. {elapsed=}")


class ModelProviderService:
    def __init__(self, settings: Settings, client: aiohttp_retry.RetryClient) -> None:
        self.api_url = settings.provider_api_url
        self.client = client

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.__aexit__(*args, **kwargs)

    def _build_url(self, path: str, **params) -> str:
        if params:
            path = f"{path}?{urlencode(params)}"
        return urljoin(self.api_url, path)

    async def list_categories(self) -> ModelProviderCategoryList:
        url = self._build_url("/categories")
        async with self.client.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing categories: {response=}")
                raise ModelProviderException("Error while listing categories")
            data = await response.json()
        return ModelProviderCategoryList(**data)

    async def list_models(self, provider: str, category: str):
        url = self._build_url(f"/providers/{provider}/categories/{category}/models")
        async with self.client.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing models")
            data = await response.json()
        return ModelProviderModelList(models=data)

    async def run_model(self, provider: str, model: str, params: dict, version: str | None = None):
        url = self._build_url(f"/providers/{provider}/models/{model}/run", version=version)
        async with self.client.post(url, json={'input': params}) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()

    async def run_model_async(self, provider: str, model: str, params: dict, version: str | None = None):
        url = self._build_url(f"/providers/{provider}/models/{model}/run_async", version=version)
        async with self.client.post(url, json={'input': params}) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            return await response.json()


def get_retry_options(settings: Annotated[Settings, Depends(get_settings)]) -> aiohttp_retry.ExponentialRetry:
    return aiohttp_retry.ExponentialRetry(
            attempts=settings.provider_api_retry_attempts,
            factor=settings.provider_api_factor,
        )

def get_trace_configs() -> list[aiohttp.TraceConfig]:
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)

    return [trace_config]

async def get_session(trace_configs: Annotated[list[aiohttp.TraceConfig], Depends(get_trace_configs)]) -> aiohttp.ClientSession:
    return aiohttp.ClientSession(trace_configs=trace_configs)

async def get_retry_client(
        session: Annotated[aiohttp.ClientSession, Depends(get_session)],
        retry_options: Annotated[aiohttp_retry.RetryOptionsBase, Depends(get_retry_options)],
) -> aiohttp_retry.RetryClient:
    return aiohttp_retry.RetryClient(client_session=session, retry=retry_options)


async def get_model_provider_service(
        settings: Annotated[Settings, Depends(get_settings)],
        client: Annotated[aiohttp_retry.RetryClient, Depends(get_retry_client)]
):
    async with ModelProviderService(settings, client) as service:
        yield service
