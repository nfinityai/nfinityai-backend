from sqlmodel import select

from backend_api.backend.session import AsyncSession
from backend_api.models.balance import Transaction as TransactionModel, TransactionType
from backend_api.schemas.balance import Transaction as TransactionSchema
from backend_api.services.balance import BalanceService

from .base import BaseDataManager, BaseService


class TransactionService(BaseService[TransactionModel]):
    def __init__(self, session: AsyncSession, balance_service: BalanceService) -> None:
        super().__init__(session)
        self.balance_service = balance_service

    async def get_transaction(self, id: int) -> TransactionSchema:
        return await TransactionDataManager(self.session).get_transaction(id)
    
    async def create_transaction(self, transaction: TransactionSchema) -> TransactionSchema:
        transaction = await TransactionDataManager(self.session).create_transaction(transaction)

        if transaction.transaction_type == TransactionType.CREDIT:
            await self.balance_service.add_amount(transaction.user_id, transaction.amount)
        else:
            await self.balance_service.remove_amount(transaction.user_id, transaction.amount)

        return transaction


class TransactionDataManager(BaseDataManager[TransactionModel]):
    async def get_transaction(self, id: int) -> TransactionSchema:
        stmt = select(TransactionModel).where(TransactionModel.id == id)

        model = await self.get_one(stmt)
        return TransactionSchema(**model.model_dump())
    
    async def create_transaction(self, transaction: TransactionSchema):
        model = await self.add_one(TransactionModel(**transaction.model_dump()))
        return TransactionSchema(**model.model_dump())
