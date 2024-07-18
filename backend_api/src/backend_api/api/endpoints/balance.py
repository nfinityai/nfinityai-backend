from typing_extensions import Annotated
from fastapi import APIRouter, Depends

from backend_api.models.balance import TransactionType
from backend_api.schemas.auth import VerifyModel
from backend_api.schemas.balance import (
    BalanceModel as BalanceModelSchema,
)
from backend_api.schemas.balance import (
    CreateTransaction as CreateTransactionSchema,
)
from backend_api.schemas.balance import (
    SiweBalanceModel,
)
from backend_api.schemas.users import User as UserSchema
from backend_api.services.auth import get_current_user
from backend_api.services.balance import BalanceService, get_balance_service
from backend_api.services.transaction import TransactionService, get_transaction_service
from backend_api.utils import create_siwe_message, verify_siwe_message

router = APIRouter()


@router.get("/balance/message", response_model=SiweBalanceModel)
async def create_message(
    amount: float,
    user: UserSchema = Depends(get_current_user),
):
    msg = create_siwe_message(
        user.wallet_address,
        statement=f"Popup balance of {user.wallet_address} for ${amount}",
    )
    return SiweBalanceModel(message=msg)


@router.get("/balance", response_model=BalanceModelSchema)
async def get_balance(
    current_user: UserSchema = Depends(get_current_user),
    balance_service: BalanceService = Depends(get_balance_service),
):
    balance = await balance_service.get_balance(current_user.id)
    return BalanceModelSchema(**balance.model_dump())


@router.post("/balance/popup", response_model=BalanceModelSchema)
async def popup_balance(
    amount: float,
    verify: Annotated[VerifyModel, Depends(verify_siwe_message)],
    current_user: UserSchema = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
    balance_service: BalanceService = Depends(get_balance_service),
):
    await transaction_service.create_transaction(
        CreateTransactionSchema(
            user_id=current_user.id, amount=amount, type=TransactionType.CREDIT
        )
    )
    balance = await balance_service.get_balance(current_user.id)
    return BalanceModelSchema(**balance.model_dump())
