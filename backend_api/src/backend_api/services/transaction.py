
from sqlmodel import select

from backend_api.backend.session import AsyncSession
from backend_api.exceptions import BalanceNotFoundError, InsufficientFundsError
from backend_api.models.balance import (
    Transaction as TransactionModel,
)
from backend_api.models.balance import (
    TransactionType,
)
from backend_api.schemas.balance import (
    CreateTransaction as CreateTransactionSchema,
)
from backend_api.schemas.balance import (
    Transaction as TransactionSchema,
)
from backend_api.schemas.balance import (
    UpdateTransactionCompleted as UpdateTransactionCompletedSchema,
)
from backend_api.schemas.balance import (
    UpdateTransactionFailed as UpdateTransactionFailedSchema,
)
from backend_api.services.balance import BalanceService

from .base import BaseDataManager, BaseService


class TransactionService(BaseService[TransactionModel]):
    def __init__(self, session: AsyncSession, balance_service: BalanceService) -> None:
        super().__init__(session)
        self.balance_service = balance_service

    async def get_transaction(self, id: int) -> TransactionSchema:
        return await TransactionDataManager(self.session).get_transaction(id)

    async def create_transaction(
        self, transaction: CreateTransactionSchema
    ) -> TransactionSchema:
        data_manager = TransactionDataManager(self.session)
        transaction = await data_manager.create_transaction(transaction)

        try:
            if transaction.type == TransactionType.CREDIT:
                await self.balance_service.add_amount(
                    transaction.user_id, transaction.amount
                )
            else:
                await self.balance_service.remove_amount(
                    transaction.user_id, transaction.amount
                )
        except (BalanceNotFoundError, InsufficientFundsError):
            return await data_manager.update_transaction(
                UpdateTransactionFailedSchema(**transaction.model_dump())
            )

        return await data_manager.update_transaction(
            UpdateTransactionCompletedSchema(**transaction.model_dump())
        )


class TransactionDataManager(BaseDataManager[TransactionModel]):
    async def get_transaction(self, id: int) -> TransactionSchema:
        stmt = select(TransactionModel).where(TransactionModel.id == id)

        model = await self.get_one(stmt)
        return TransactionSchema(**model.model_dump())

    async def create_transaction(
        self, transaction: CreateTransactionSchema
    ) -> TransactionSchema:
        model = await self.add_one(TransactionModel(**transaction.model_dump()))
        return TransactionSchema(**model.model_dump())

    async def update_transaction(
        self,
        transaction: UpdateTransactionCompletedSchema | UpdateTransactionFailedSchema,
    ) -> TransactionSchema:
        model = await self.add_one(TransactionModel(**transaction.model_dump()))
        return TransactionSchema(**model.model_dump())
