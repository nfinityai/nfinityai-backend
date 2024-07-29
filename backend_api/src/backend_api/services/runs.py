from typing import Annotated

from fastapi import Depends

from backend_api.backend.config import Settings, get_settings
from backend_api.backend.logging import get_logger
from backend_api.schemas.auth import VerifyModel
from backend_api.schemas.model_providers import (
    ModelProviderModelRunAsync,
    ModelProviderModelRunResult,
    ModelRunQuery,
)
from backend_api.schemas.usage import CreateUsage
from backend_api.schemas.users import User as UserSchema
from backend_api.services.model_providers import (
    ModelProviderException,
    ModelProviderService,
    get_model_provider_service,
)
from backend_api.services.usage import UsageService, get_usage_service

logger = get_logger(__name__)


class RunModelException(Exception):
    pass


class RunService:
    def __init__(
        self,
        settings: Settings,
        model_provider_service: ModelProviderService,
        usage_service: UsageService,
    ):
        self.settings = settings
        self.model_provider_service = model_provider_service
        self.usage_service = usage_service

    async def run_model(
        self,
        user: UserSchema,
        verify: VerifyModel,
        model: str,
        run_query: ModelRunQuery,
        version: str | None = None,
    ) -> ModelProviderModelRunResult:
        logger.info(
            "Run model started",
            provider=self.settings.provider,
            user=user,
            model=model,
            run_query=run_query,
        )
        try:
            run = await self.model_provider_service.run_model(
                self.settings.provider, model, run_query.input, version
            )
        except ModelProviderException as e:
            logger.error("Unable to get result from model run", exc_info=e)
            raise RunModelException("Unable to run model") from e
        logger.info(
            "Run model successfully finished",
            provider=self.settings.provider,
            user=user,
            model=model,
            run=run,
        )

        await self.track_usage(
            model,
            user,
            run.result.elapsed_time,
            verify.signature,
        )

        return run

    async def run_model_async(
        self,
        user: UserSchema,
        verify: VerifyModel,
        model: str,
        run_query: ModelRunQuery,
        version: str | None = None,
    ) -> ModelProviderModelRunAsync:
        try:
            run = await self.model_provider_service.run_model_async(
                self.settings.provider, model, run_query.input, version
            )
        except ModelProviderException as e:
            logger.error("Unable to run model asynchronically", exc_info=e)
            raise RunModelException("Unable to run model asynchronically") from e

        # track usage
        await self.track_usage(
            model,
            user,
            elapsed_time=None,
            signature=verify.signature,
        )

        return run

    async def get_run_status(self, run_id: str):
        try:
            return await self.model_provider_service.run_model_async_status(run_id)
        except ModelProviderException as e:
            logger.error("Unable to get run status", exc_info=e)
            raise RunModelException("Unable to get run status") from e

    async def get_run_result(self, run_id: str):
        try:
            return await self.model_provider_service.run_model_async_result(run_id)
        except ModelProviderException as e:
            logger.error("Unable to get run result", exc_info=e)
            raise RunModelException("Unable to get run result") from e

    async def _calculate_cost(
        self, provider: str, model: str, elapsed_time: float | None
    ) -> float:
        model_costs = await self.model_provider_service.get_model_costs(provider, model)
        if elapsed_time is None:
            elapsed_time = model_costs.info.prediction_time
        hardware_costs = await self.model_provider_service.get_hardware_costs(provider)
        for hardware in filter(
            lambda x: x.sku == model_costs.info.sku, hardware_costs.info
        ):
            cost = hardware.price_per_second * elapsed_time
            return cost
        return self.settings.default_model_cost

    async def track_usage(
        self,
        model: str,
        user: UserSchema,
        elapsed_time: float | None,
        signature: str,
    ):
        return await self.usage_service.create_usage(
            CreateUsage(
                user_id=user.id,
                credits_spent=await self._calculate_cost(
                    self.settings.provider, model, elapsed_time
                ),
                request_signature=signature,
            )
        )


async def get_run_service(
    settings: Annotated[Settings, Depends(get_settings)],
    model_provider_service: Annotated[
        ModelProviderService, Depends(get_model_provider_service)
    ],
    usage_service: Annotated[UsageService, Depends(get_usage_service)],
):
    return RunService(
        settings=settings,
        model_provider_service=model_provider_service,
        usage_service=usage_service,
    )
