from typing_extensions import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend_api.backend.config import Settings, get_settings
from backend_api.schemas.auth import VerifyModel
from backend_api.schemas.model_providers import (
    ModelProviderModelRunAsync,
    ModelProviderModelRunAsyncResult,
    ModelProviderModelRunAsyncStatus,
)
from backend_api.schemas.runs import SiweRunModel
from backend_api.schemas.users import User as UserSchema
from backend_api.schemas.model_providers import (
    ModelProviderModelRunResult as ModelProviderModelRunResultSchema,
)
from backend_api.services.auth import get_current_user
from backend_api.services.model_providers import (
    ModelProviderService,
    get_model_provider_service,
)
from backend_api.utils import create_siwe_message, verify_siwe_message

router = APIRouter(dependencies=[Depends(get_current_user)])


class ModelRunQuery(BaseModel):
    input: dict


@router.get("/{model}/message", response_model=SiweRunModel)
async def create_message(
    model: str,
    user: UserSchema = Depends(get_current_user),
):
    msg = create_siwe_message(
        user.wallet_address,
        statement=f"Run model {model}",
    )
    return SiweRunModel(message=msg)


@router.post("/{model}", response_model=ModelProviderModelRunResultSchema)
async def run_model(
    model: str,
    run_query: ModelRunQuery,
    verify: Annotated[VerifyModel, Depends(verify_siwe_message)],
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
    user: UserSchema = Depends(get_current_user),
    version: str | None = None,
):
    run = await model_provider_service.run_model(
        settings.provider, model, run_query.input, version
    )
    # track usage
    await model_provider_service.track_usage(
        settings.provider, model, user, run.result.elapsed_time, verify.signature
    )

    return run


@router.post("/async/{model}", response_model=ModelProviderModelRunAsync)
async def run_model_async(
    model: str,
    run_query: ModelRunQuery,
    verify: Annotated[VerifyModel, Depends(verify_siwe_message)],
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
    user: UserSchema = Depends(get_current_user),
    version: str | None = None,
):
    run = await model_provider_service.run_model_async(
        settings.provider, model, run_query.input, version
    )
    # track usage
    await model_provider_service.track_usage(
        settings.provider, model, user, elapsed_time=None, signature=verify.signature
    )

    return run


@router.get("/{run_id}/status", response_model=ModelProviderModelRunAsyncStatus)
async def get_run_status(
    run_id: str,
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
):
    return await model_provider_service.run_model_async_status(run_id)


@router.get("/{run_id}/result", response_model=ModelProviderModelRunAsyncResult)
async def get_run_result(
    run_id: str,
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
):
    return await model_provider_service.run_model_async_result(run_id)
