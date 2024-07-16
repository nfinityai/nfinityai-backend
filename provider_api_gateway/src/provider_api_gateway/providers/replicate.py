from typing import Annotated
from fastapi import Depends
from replicate import async_paginate
from replicate.collection import Collection
from replicate.model import Model
from replicate.client import Client
import replicate

from provider_api_gateway.config import Settings, get_settings
from provider_api_gateway.providers.base import BaseProvider
from provider_api_gateway.schemas.types import ProviderEnum
from provider_api_gateway.schemas.categories import Category


class ReplicateClient(BaseProvider, Client):
    PROVIDER_ID = ProviderEnum.REPLICATE

    async def list_categories(self) -> list[Category]:
        categories = []
        async for page in async_paginate(self.collections.async_list):
            for collection in page:
                categories.append(Category(provider=ReplicateClient.PROVIDER_ID, **collection.dict()))
        return categories

    async def list_models(self, collection_slug: str) -> list[Model]:
        models = self.collections.get(collection_slug).models
        if not models:
            return []
        return models
    
    async def get_latest_model_version(self, model_slug: str):
        model = self.models.get(model_slug)
        return model.latest_version
    

    async def run_model(self, model_slug: str, input_params: dict):
        model_version = await self.get_latest_model_version(model_slug)
        ref = f"{model_slug}"
        if model_version:
            ref = f"{model_slug}:{model_version}"
        result = await replicate.async_run(ref, input=input_params)
        return result


def get_replicate_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReplicateClient:
    return ReplicateClient(api_token=settings.replicate_api_key)
