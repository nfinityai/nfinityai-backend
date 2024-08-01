from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException

from backend_api.schemas.auth import VerifyModel
from backend_api.schemas.model_providers import (
    ModelProviderModelRunAsync,
    ModelProviderModelRunAsyncResult,
    ModelProviderModelRunAsyncStatus,
    ModelRunQuery,
)
from backend_api.schemas.runs import SiweRunModel
from backend_api.schemas.users import User as UserSchema
from backend_api.schemas.model_providers import (
    ModelProviderModelRunResult as ModelProviderModelRunResultSchema,
)
from backend_api.services.auth import get_current_user
from backend_api.services.balance import BalanceService, get_balance_service
from backend_api.services.runs import RunService, get_run_service
from backend_api.utils import create_siwe_message, verify_siwe_message

router = APIRouter(dependencies=[Depends(get_current_user)])


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
    run_service: RunService = Depends(get_run_service),
    user: UserSchema = Depends(get_current_user),
    version: str | None = None,
    balance_service: BalanceService = Depends(get_balance_service),
):
    if not await balance_service.has_sufficient_balance(user_id=user.id, required_amount=1):
        raise HTTPException(status_code=400, detail="Insufficient balance to run the model")
    return await run_service.run_model(user, verify, model, run_query, version)


@router.post("/async/{model}", response_model=ModelProviderModelRunAsync)
async def run_model_async(
    model: str,
    run_query: ModelRunQuery,
    verify: Annotated[VerifyModel, Depends(verify_siwe_message)],
    run_service: RunService = Depends(get_run_service),
    user: UserSchema = Depends(get_current_user),
    version: str | None = None,
    balance_service: BalanceService = Depends(get_balance_service),
):
    if not await balance_service.has_sufficient_balance(user_id=user.id, required_amount=1):
        raise HTTPException(status_code=400, detail="Insufficient balance to run the model")
    return await run_service.run_model_async(user, verify, model, run_query, version)


@router.get("/{run_id}/status", response_model=ModelProviderModelRunAsyncStatus)
async def get_run_status(
    run_id: str,
    run_service: RunService = Depends(get_run_service),
):
    return await run_service.get_run_status(run_id)


@router.get("/{run_id}/result", response_model=ModelProviderModelRunAsyncResult)
async def get_run_result(
    run_id: str,
    run_service: RunService = Depends(get_run_service),
):
    return await run_service.get_run_result(run_id)
