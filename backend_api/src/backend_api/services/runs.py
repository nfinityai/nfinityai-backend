from typing import Annotated

from fastapi import Depends, HTTPException

from backend_api.backend.config import Settings, get_settings
from backend_api.backend.logging import get_logger
from backend_api.backend.session import get_session
from backend_api.schemas.auth import VerifyModel
from backend_api.schemas.model_providers import (
    ModelProviderModelRunAsync,
    ModelProviderModelRunResult,
    ModelRunQuery,
)
from backend_api.schemas.models import Model
from backend_api.schemas.usage import CreateUsage
from backend_api.schemas.users import User as UserSchema
from backend_api.services.balance import BalanceService
from backend_api.services.model_providers import (
    ModelProviderException,
    ModelProviderService,
    get_model_provider_service,
)
from backend_api.services.models import ModelService, get_model_service
from backend_api.services.usage import UsageService, get_usage_service
from backend_api.services.web3 import Web3Service, get_web3_service

logger = get_logger(__name__)


class RunModelException(Exception):
    pass


class RunService:
    def __init__(
        self,
        settings: Settings,
        model_provider_service: ModelProviderService,
        usage_service: UsageService,
        web3_service: Web3Service,
    ):
        self.settings = settings
        self.model_provider_service = model_provider_service
        self.usage_service = usage_service
        self.web3_service = web3_service

    async def run_model(
        self,
        user: UserSchema,
        verify: VerifyModel,
        balance_service: BalanceService,
        model: str,
        run_query: ModelRunQuery,
        version: str | None = None,
    ) -> ModelProviderModelRunResult:
        if not await self.web3_service.has_sufficient_balance(user.wallet_address, 10000):
            logger.error(
                "Insufficient NFNT balance to run the model",
                provider=self.settings.provider,
                user=user,
                model=model,
                run_query=run_query,
            )
            raise HTTPException(
                status_code=400, detail="Insufficient NFNT balance to run the model"
            )

        if not await balance_service.has_sufficient_balance(user_id=user.id, required_amount=1):
            logger.error(
                "Insufficient balance to run the model",
                provider=self.settings.provider,
                user=user,
                model=model,
                run_query=run_query,
            )
            raise HTTPException(status_code=400, detail="Insufficient balance to run the model")
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
        balance_service: BalanceService,
        model: str,
        run_query: ModelRunQuery,
        version: str | None = None,
    ) -> ModelProviderModelRunAsync:
        if not await self.web3_service.has_sufficient_balance(user.wallet_address, 10000):
            logger.error(
                "Insufficient NFNT balance to run the model",
                provider=self.settings.provider,
                user=user,
                model=model,
                run_query=run_query,
            )
            raise HTTPException(
                status_code=400, detail="Insufficient NFNT balance to run the model"
            )
        if not await balance_service.has_sufficient_balance(user_id=user.id, required_amount=1):
            logger.error(
                "Insufficient balance to run the model",
                provider=self.settings.provider,
                user=user,
                model=model,
                run_query=run_query,
            )
            raise HTTPException(status_code=400, detail="Insufficient balance to run the model")
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

    async def _calculate_cost(self, provider: str, model: str, elapsed_time: float | None) -> float:
        model_costs = await self.model_provider_service.get_model_costs(provider, model)
        if elapsed_time is None:
            elapsed_time = model_costs.info.prediction_time
        hardware_costs = await self.model_provider_service.get_hardware_costs(provider)
        for hardware in filter(lambda x: x.sku == model_costs.info.sku, hardware_costs.info):
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
        model_slug = model
        async for session in get_session():
            service: ModelService = await get_model_service(session)
            model: Model = await service.get_model_by_slug(model_slug)
            return await self.usage_service.create_usage(
                CreateUsage(
                    user_id=user.id,
                    credits_spent=await self._calculate_cost(
                        self.settings.provider, model_slug, elapsed_time
                    ),
                    request_signature=signature,
                    model_id=model.id,
                )
            )


async def get_run_service(
    settings: Annotated[Settings, Depends(get_settings)],
    model_provider_service: Annotated[ModelProviderService, Depends(get_model_provider_service)],
    usage_service: Annotated[UsageService, Depends(get_usage_service)],
    web3_service: Annotated[Web3Service, Depends(get_web3_service)],
):
    return RunService(
        settings=settings,
        model_provider_service=model_provider_service,
        usage_service=usage_service,
        web3_service=web3_service,
    )
