from typing import Annotated

import replicate
from fastapi import Depends
from replicate import async_paginate
from replicate.client import Client

from provider_api_gateway.config import Settings, get_settings
from provider_api_gateway.providers.base import BaseProvider
from provider_api_gateway.schemas.categories import ProviderModelCategory
from provider_api_gateway.schemas.models import ProviderModel
from provider_api_gateway.schemas.types import ProviderEnum
from provider_api_gateway.utils import decode_string, measured
from provider_api_gateway.logging import get_logger

logger = get_logger(__name__)


class ReplicateClient(BaseProvider, Client):
    PROVIDER_ID = ProviderEnum.REPLICATE

    async def list_categories(self) -> list[ProviderModelCategory]:
        categories = []
        async for page in async_paginate(self.collections.async_list):
            for collection in page:
                categories.append(
                    ProviderModelCategory.from_provider_model(
                        ReplicateClient.PROVIDER_ID, collection
                    )
                )
        return categories

    async def list_models(
        self, collection_slug: str, public_only=True
    ) -> list[ProviderModel]:
        collection = await self.collections.async_get(collection_slug)
        if not collection.models:
            return []
        models = []

        for model in collection.models:
            if public_only and model.visibility != "public":
                continue
            models.append(model)

        return [ProviderModel(**model.dict()) for model in models]

    async def run_model(self, model_slug: str, model_version: str | None, input_params: dict):
        """Run a model from the Replicate provider."""
        model = decode_string(model_slug)
        if model_version is not None:
            model = f"{model}:{model_version}"
        logger.info("Running model", model=model, input=input_params)
        result = await self._run_model(model, input_params)
        output, execution_time = result  # type: ignore
        logger.info("Model finished", model=model, execution_time=execution_time, output=output)
        return output
    
    @measured
    async def _run_model(self, ref, input, **kwargs):
        return await replicate.async_run(ref, input=input, **kwargs)


def get_replicate_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReplicateClient:
    return ReplicateClient(api_token=settings.replicate_api_token)
