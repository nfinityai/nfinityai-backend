from fastapi import Depends
from sqlmodel import select
from typing_extensions import Annotated

from backend_api.backend.session import AsyncSession, get_session
from backend_api.exceptions import BalanceNotFoundError, InsufficientFundsError
from backend_api.models.balance import Balance as BalanceModel
from backend_api.schemas.balance import Balance as BalanceSchema
from backend_api.schemas.balance import CreateBalance as CreateBalanceSchema

from .base import BaseDataManager, BaseService


class BalanceService(BaseService[BalanceModel]):
    async def get_balance(self, user_id: int) -> BalanceSchema:
        return await BalanceDataManager(self.session).get_balance(user_id)

    async def create_balance(self, balance: CreateBalanceSchema) -> BalanceSchema:
        return await BalanceDataManager(self.session).add_balance(balance)

    async def add_amount(self, user_id: int, amount: float):
        return await BalanceDataManager(self.session).add_amount(user_id, amount)

    async def remove_amount(self, user_id: int, amount: float):
        return await BalanceDataManager(self.session).remove_amount(user_id, amount)

    async def has_sufficient_balance(self, user_id: int, required_amount: float) -> bool:
        try:
            balance = await self.get_balance(user_id)
            return balance.amount > required_amount
        except BalanceNotFoundError:
            return False


class BalanceDataManager(BaseDataManager[BalanceModel]):
    async def get_balance(self, user_id: int) -> BalanceSchema:
        stmt = select(BalanceModel).where(BalanceModel.user_id == user_id)

        model = await self.get_one(stmt)
        return BalanceSchema(**model.model_dump())

    async def add_balance(self, balance: CreateBalanceSchema) -> BalanceSchema:
        model = await self.add_one(BalanceModel(**balance.model_dump()))

        return BalanceSchema(**model.model_dump())

    async def add_amount(self, user_id: int, amount: float):
        stmt = select(BalanceModel).where(BalanceModel.user_id == user_id)
        model = await self.get_one(stmt)

        if not model:
            model = BalanceModel(user_id=user_id, amount=amount)
            await self.add_one(model)
        else:
            model.amount += amount

        await self.session.commit()
        await self.session.refresh(model)

    async def remove_amount(self, user_id: int, amount: float):
        stmt = select(BalanceModel).where(BalanceModel.user_id == user_id)
        model = await self.get_one(stmt)

        if not model:
            raise BalanceNotFoundError("Unable to remove funds")

        model.amount -= amount
        if model.amount < 0:
            raise InsufficientFundsError("Insufficient balance")

        await self.session.commit()
        await self.session.refresh(model)


async def get_balance_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BalanceService:
    return BalanceService(session)
