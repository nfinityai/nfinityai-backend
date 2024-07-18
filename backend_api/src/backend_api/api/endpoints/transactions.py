from fastapi import APIRouter, Depends

from backend_api.schemas.users import User as UserModel
from backend_api.services.auth import get_current_user
from backend_api.schemas.balance import (
    TransactionList as TransactionListSchema,
)
from backend_api.services.transaction import TransactionService, get_transaction_service

router = APIRouter()


@router.get("/transactions", response_model=TransactionListSchema)
async def get_transactions(
    current_user: UserModel = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    transactions = await transaction_service.get_transactions(current_user.id)
    return TransactionListSchema(transactions=transactions)
