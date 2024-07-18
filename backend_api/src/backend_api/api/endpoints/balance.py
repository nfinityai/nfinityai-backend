from fastapi import APIRouter, Depends

from backend_api.models.balance import TransactionType
from backend_api.schemas.balance import BalanceModel as BalanceModelSchema
from backend_api.schemas.users import User as UserModel
from backend_api.services.auth import get_current_user
from backend_api.services.balance import BalanceService, get_balance_service
from backend_api.schemas.balance import (
    CreateTransaction as CreateTransactionSchema,
)
from backend_api.services.transaction import TransactionService, get_transaction_service

router = APIRouter()


@router.get("/balance", response_model=BalanceModelSchema)
async def get_balance(
    current_user: UserModel = Depends(get_current_user),
    balance_service: BalanceService = Depends(get_balance_service),
):
    balance = await balance_service.get_balance(current_user.id)
    return BalanceModelSchema(**balance.model_dump())


@router.get("/balance/popup", response_model=BalanceModelSchema)
async def popup_balance(
    amount: float,
    current_user: UserModel = Depends(get_current_user),
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
