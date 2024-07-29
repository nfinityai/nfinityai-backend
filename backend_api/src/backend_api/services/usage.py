import asyncio
from typing import Annotated
from fastapi import Depends
from sqlmodel import select

from backend_api.backend.session import AsyncSession, get_session
from backend_api.exceptions.balance import (
    TransactionFailedError,
    TransactionUncompletedError,
)
from backend_api.models.balance import TransactionStatus, TransactionType
from backend_api.models.usage import Usage as UsageModel
from backend_api.schemas.usage import CreateUsage, Usage as UsageSchema
from backend_api.services.transaction import TransactionService, get_transaction_service
from backend_api.schemas.balance import CreateTransaction as CreateTransactionSchema

from .base import BaseDataManager, BaseService


class UsageService(BaseService[UsageModel]):
    def __init__(self, session: AsyncSession, transaction_service: TransactionService) -> None:
        super().__init__(session)
        self.transaction_service = transaction_service

    async def get_usage(self, usage_id: int) -> UsageSchema:
        return await UsageDataManager(self.session).get_usage(usage_id)

    async def get_usage_by_user(self, user_id: int) -> list[UsageSchema]:
        return await UsageDataManager(self.session).get_usage_by_user(user_id)

    async def create_usage(self, create_usage: CreateUsage) -> UsageSchema:
        transaction = await self.transaction_service.create_transaction(
            CreateTransactionSchema(
                user_id=create_usage.user_id,
                amount=create_usage.credits_spent,
                type=TransactionType.DEBIT,
                status=TransactionStatus.PENDING,
            )
        )
        # TODO Add method to check status from replicate.
        if transaction.status == TransactionStatus.COMPLETED or TransactionStatus.PENDING:
            usage_dict = create_usage.dict()
            usage_dict.update(
                {
                    "transaction_id": transaction.id,
                }
            )
            updated_usage = CreateUsage(**usage_dict)
            return await UsageDataManager(self.session).add_usage(updated_usage)
        elif transaction.status == TransactionStatus.FAILED:
            raise TransactionFailedError("Transaction status is failed")

        raise TransactionUncompletedError("Transaction status is uncompleted")


class UsageDataManager(BaseDataManager[UsageModel]):
    async def get_usage(self, usage_id: int) -> UsageSchema:
        stmt = select(UsageModel).where(UsageModel.id == usage_id)

        model = await self.get_one(stmt)
        return UsageSchema(**model.model_dump())

    async def get_usage_by_user(self, user_id: int) -> list[UsageSchema]:
        stmt = select(UsageModel).where(UsageModel.user_id == user_id)

        models = await self.get_all(stmt)
        return [UsageSchema(**model.model_dump()) for model in models]

    async def add_usage(self, usage: CreateUsage) -> UsageSchema:
        model = await self.add_one(UsageModel(**usage.model_dump()))
        return UsageSchema(**model.model_dump())


async def get_usage_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> UsageService:
    return UsageService(session, transaction_service)
