from enum import Enum
from typing import Annotated, Any

from fastapi import Depends
from replicate import async_paginate
from replicate.client import Client
from replicate.exceptions import ModelError as ReplicateModelError
from replicate.model import Model
from replicate.version import Version

from provider_api_gateway.config import Settings, get_settings
from provider_api_gateway.logging import get_logger
from provider_api_gateway.providers.base import BaseProvider
from provider_api_gateway.providers.exceptions import ReplicateClientError
from provider_api_gateway.schemas.categories import ProviderModelCategory
from provider_api_gateway.schemas.models import ProviderHardwareCost, ProviderModel, ProviderModelCost
from provider_api_gateway.schemas.runs import Run, RunResult, RunResultModel, RunStatus
from provider_api_gateway.schemas.types import ProviderEnum
from provider_api_gateway.services.extractors.replicate import (
    ReplicateHardwareCostExtractor,
    ReplicateModelCostExtractor,
    get_cost_table_extractor,
    get_replicate_model_cost_extractor,
)
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

    def __init__(
        self,
        model_cost_extractor: ReplicateModelCostExtractor,
        hardware_cost_extractor: ReplicateHardwareCostExtractor,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.model_cost_extractor = model_cost_extractor
        self.hardware_cost_extractor = hardware_cost_extractor

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
    ) -> RunResultModel:
        """Run a model from the Replicate provider."""
        model = decode_string(model_slug)
        if model_version is not None:
            model = f"{model}:{model_version}"
        logger.info("Running model", model=model, input=input_params)
        output, execution_time = await self._run_model(model, input_params)
        logger.info(
            "Model finished", model=model, execution_time=execution_time, output=output
        )
        return output  # type: ignore

    @measured
    async def _run_model(self, ref: Any, input: dict, **kwargs):
        try:
            output = await self.async_run(ref, input=input, **kwargs)
            return RunResultModel(output=output)
        except ReplicateModelError as e:
            logger.error("Unable to get result", model=ref, input=input, error=e)
            return RunResultModel(error=str(e))

    # async model run

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
            result = RunResultModel(**prediction.dict())
            return RunResult(result=result, **prediction.dict())

        # TODO: handle other states
        return RunResult(**prediction.dict())

    # hardware specs

    async def get_hardware_list(self):
        return await self.hardware.async_list()

    # cost info

    async def get_model_cost_info(self, model_slug: str) -> ProviderModelCost:
        model = await self.models.async_get(decode_string(model_slug))
        info = await self.model_cost_extractor.get_run_time_and_cost(model.url)

        return ProviderModelCost(info=info)
    
    async def get_hardware_cost_info(self, url: str) -> ProviderHardwareCost:
        info = await self.hardware_cost_extractor.extract_cost_info(url)

        return ProviderHardwareCost(info=info.to_dict(orient='records') if info is not None else None)


def get_replicate_client(
    settings: Annotated[Settings, Depends(get_settings)],
    model_cost_extractor: Annotated[
        ReplicateModelCostExtractor, Depends(get_replicate_model_cost_extractor)
    ],
    hardware_cost_extractor: Annotated[
        ReplicateHardwareCostExtractor, Depends(get_cost_table_extractor)
    ],
) -> ReplicateClient:
    return ReplicateClient(
        model_cost_extractor,
        hardware_cost_extractor,
        api_token=settings.replicate_api_token,
    )
