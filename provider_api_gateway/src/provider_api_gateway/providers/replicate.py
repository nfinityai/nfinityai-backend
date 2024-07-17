from enum import Enum
from typing import Annotated, Any

from fastapi import Depends
from replicate import async_paginate
from replicate.client import Client
from replicate.model import Model
from replicate.version import Version

from provider_api_gateway.config import Settings, get_settings
from provider_api_gateway.logging import get_logger
from provider_api_gateway.providers.base import BaseProvider
from provider_api_gateway.providers.exceptions import ReplicateClientError
from provider_api_gateway.schemas.categories import ProviderModelCategory
from provider_api_gateway.schemas.models import ProviderModel
from provider_api_gateway.schemas.runs import Run, RunResult, RunResultModel, RunStatus
from provider_api_gateway.schemas.types import ProviderEnum
from provider_api_gateway.utils import decode_string, measured

logger = get_logger(__name__)


class ReplicatePredictionState(str, Enum):
    STARTING = "starting"
    PROCESSING = "processing"
    FAILED = "failed"
    CANCELED = "canceled"
    SUCCEEDED = "succeeded"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def finished_states(cls) -> tuple[str, ...]:
        states = [cls.SUCCEEDED, cls.FAILED, cls.CANCELED]
        return tuple(state.value for state in states)


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

    async def run_model(
        self, model_slug: str, model_version: str | None, input_params: dict
    ):
        """Run a model from the Replicate provider."""
        model = decode_string(model_slug)
        if model_version is not None:
            model = f"{model}:{model_version}"
        logger.info("Running model", model=model, input=input_params)
        result = await self._run_model(model, input_params)
        output, execution_time = result  # type: ignore
        logger.info(
            "Model finished", model=model, execution_time=execution_time, output=output
        )
        return output

    @measured
    async def _run_model(self, ref: Any, input: dict, **kwargs):
        return await self.async_run(ref, input=input, **kwargs)

    async def run_model_async(
        self, model_slug: str, model_version: str | None, input_params: dict
    ) -> Run:
        """Run a model async from the Replicate provider."""
        model = self.models.get(decode_string(model_slug))
        if model_version is not None:
            version = model.versions.get(model_version)
        logger.info(
            "Running model (async)", model=model, version=version, input=input_params
        )
        result = await self._run_model_async(
            ref=model if model_version is None else version, input=input_params
        )
        output, execution_time = result  # type: ignore
        logger.info(
            "Model started", model=model, execution_time=execution_time, output=output
        )
        return Run(**output.dict())

    @measured
    async def _run_model_async(self, ref: Any, input: dict, **kwargs):
        if isinstance(ref, Version):
            return await self.predictions.async_create(ref, input=input, **kwargs)
        if isinstance(ref, Model):
            return await self.models.predictions.async_create(
                ref, input=input, **kwargs
            )
        raise ReplicateClientError("Invalid model reference")

    async def get_run_model_status(self, id: str) -> RunStatus:
        """Get the status of a model run by id."""
        prediction = self.predictions.get(id)
        logger.info("Getting status", prediction=prediction)
        return RunStatus(**prediction.dict())

    async def get_run_model_result(self, id: str) -> RunResult:
        """Get the result of a model run by id."""
        prediction = self.predictions.get(id)
        logger.info("Getting result", prediction=prediction)
        if prediction.status in ReplicatePredictionState.finished_states():
            result = RunResultModel(output=prediction.output, error=prediction.error)
            return RunResult(result=result, **prediction.dict())

        # TODO: handle other states
        return RunResult(**prediction.dict())


def get_replicate_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ReplicateClient:
    return ReplicateClient(api_token=settings.replicate_api_token)
