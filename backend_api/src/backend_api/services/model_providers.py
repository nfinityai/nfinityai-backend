from functools import lru_cache
import logging
import time
from http import HTTPStatus
from urllib.parse import urlencode, urljoin

import aiohttp
import aiohttp_retry
from fastapi import Depends
from typing_extensions import Annotated

from backend_api.backend.config import Settings, get_settings
from backend_api.schemas.model_providers import (
    ModelProviderCategoryList,
    ModelProviderHardwareCosts,
    ModelProviderModelCosts,
    ModelProviderModelList,
    ModelProviderModelRunAsync,
    ModelProviderModelRunAsyncResult,
    ModelProviderModelRunAsyncStatus,
    ModelProviderModelRunResult,
)

logger = logging.getLogger(__name__)


class ModelProviderException(Exception):
    pass


async def on_request_start(session, trace_config_ctx, params):
    trace_config_ctx.start = time.time()


async def on_request_end(session, trace_config_ctx, params):
    elapsed = time.time() - trace_config_ctx.start
    logger.info(f"Request to api finished. {elapsed=}")


class ModelProviderService:
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self.api_url = settings.provider_api_url
        self.settings = settings
        self.init_client()

    def init_client(self):
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)
        session = aiohttp.ClientSession(trace_configs=[trace_config])
        retry_options = aiohttp_retry.ExponentialRetry(
            attempts=self.settings.provider_api_retry_attempts,
            factor=self.settings.provider_api_factor,
        )
        self.client = aiohttp_retry.RetryClient(
            client_session=session, retry=retry_options
        )

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

    async def list_models(self, provider: str, category: str) -> ModelProviderModelList:
        url = self._build_url(f"/providers/{provider}/categories/{category}/models")
        async with self.client.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing models")
            data = await response.json()
        return ModelProviderModelList(models=data)

    async def run_model(
        self, provider: str, model: str, params: dict, version: str | None = None
    ) -> ModelProviderModelRunResult:
        url = self._build_url(
            f"/providers/{provider}/models/{model}/run", version=version
        )
        async with self.client.post(url, json={"input": params}) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            data = await response.json()

        return ModelProviderModelRunResult(result=data)

    async def run_model_async(
        self, provider: str, model: str, params: dict, version: str | None = None
    ) -> ModelProviderModelRunAsync:
        url = self._build_url(
            f"/providers/{provider}/models/{model}/run_async", version=version
        )
        async with self.client.post(url, json={"input": params}) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing models: {response=}")
                raise ModelProviderException("Error while listing categories")
            data = await response.json()
        return ModelProviderModelRunAsync(**data)

    async def run_model_async_status(
        self, job_id: str
    ) -> ModelProviderModelRunAsyncStatus:
        url = self._build_url(f"/runs/{job_id}/status")
        async with self.client.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing categories: {response=}")
                raise ModelProviderException("Error while listing categories")
            data = await response.json()

        return ModelProviderModelRunAsyncStatus(**data)

    async def run_model_async_result(
        self, job_id: str
    ) -> ModelProviderModelRunAsyncResult:
        url = self._build_url(f"/runs/{job_id}/result")
        async with self.client.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing categories: {response=}")
                raise ModelProviderException("Error while listing categories")
            data = await response.json()

        return ModelProviderModelRunAsyncResult(**data)

    async def get_model_costs(
        self, provider: str, model: str
    ) -> ModelProviderModelCosts:
        url = self._build_url(f"/providers/{provider}/models/{model}/info")
        async with self.client.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing categories: {response=}")
                raise ModelProviderException("Error while listing categories")
            data = await response.json()
        return ModelProviderModelCosts(**data)

    @lru_cache
    async def get_hardware_costs(self, provider: str) -> ModelProviderHardwareCosts:
        url = self._build_url(f"/providers/{provider}/hardware/costs")
        async with self.client.get(url) as response:
            if response.status != HTTPStatus.OK:
                logger.error(f"Error while listing categories: {response=}")
                raise ModelProviderException("Error while listing categories")
            data = await response.json()
        return ModelProviderHardwareCosts(**data)


async def get_model_provider_service(
    settings: Annotated[Settings, Depends(get_settings)],
):
    async with ModelProviderService(settings) as service:
        yield service
