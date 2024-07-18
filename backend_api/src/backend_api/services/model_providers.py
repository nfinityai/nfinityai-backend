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
from backend_api.schemas.usage import CreateUsage
from backend_api.schemas.users import User as UserSchema
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
from backend_api.services.usage import UsageService, get_usage_service

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
        client: aiohttp_retry.RetryClient,
        usage_service: UsageService,
    ) -> None:
        self.api_url = settings.provider_api_url
        self.settings = settings
        self.client = client
        self.usage_service = usage_service

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
    
    async def _calculate_cost(self, provider: str, model: str, elapsed_time: float | None) -> float:
        model_costs = await self.get_model_costs(provider, model)
        if elapsed_time is None:
            elapsed_time = model_costs.info.prediction_time
        hardware_costs = await self.get_hardware_costs(provider)
        for hardware in filter(lambda x: x.sku == model_costs.info.sku, hardware_costs.info):
            cost = hardware.price_per_second * elapsed_time
            return cost
        return self.settings.default_model_cost
        
    async def _build_usage(self, provider: str, model:str, user: UserSchema, elapsed_time: float | None, signature: str):
        cost = await self._calculate_cost(provider, model, elapsed_time)
        return CreateUsage(
            user_id=user.id,
            credits_spent=cost,
            request_signature=signature
        )
    
    async def track_usage(self, usage: CreateUsage):
        return await self.usage_service.create_usage(usage)



def get_retry_options(
    settings: Annotated[Settings, Depends(get_settings)],
) -> aiohttp_retry.ExponentialRetry:
    return aiohttp_retry.ExponentialRetry(
        attempts=settings.provider_api_retry_attempts,
        factor=settings.provider_api_factor,
    )


def get_trace_configs() -> list[aiohttp.TraceConfig]:
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)

    return [trace_config]


async def get_session(
    trace_configs: Annotated[list[aiohttp.TraceConfig], Depends(get_trace_configs)],
) -> aiohttp.ClientSession:
    return aiohttp.ClientSession(trace_configs=trace_configs)


async def get_retry_client(
    session: Annotated[aiohttp.ClientSession, Depends(get_session)],
    retry_options: Annotated[
        aiohttp_retry.RetryOptionsBase, Depends(get_retry_options)
    ],
) -> aiohttp_retry.RetryClient:
    return aiohttp_retry.RetryClient(client_session=session, retry=retry_options)


async def get_model_provider_service(
    settings: Annotated[Settings, Depends(get_settings)],
    client: Annotated[aiohttp_retry.RetryClient, Depends(get_retry_client)],
    usage_service: Annotated[UsageService, Depends(get_usage_service)],
):
    async with ModelProviderService(settings, client, usage_service) as service:
        yield service
