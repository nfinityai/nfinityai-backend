from sqlmodel import select

from backend_api.exceptions import BalanceNotFoundError, InsufficientFundsError
from backend_api.models.balance import Balance as BalanceModel
from backend_api.schemas.balance import Balance as BalanceSchema

from .base import BaseDataManager, BaseService


class BalanceService(BaseService[BalanceModel]):
    async def get_balance(self, user_id: int) -> BalanceSchema:
        return await BalanceDataManager(self.session).get_balance(user_id)


class BalanceDataManager(BaseDataManager[BalanceModel]):
    async def get_balance(self, user_id: int) -> BalanceSchema:
        stmt = select(BalanceModel).where(BalanceModel.user_id == user_id)

        model = await self.get_one(stmt)
        return BalanceSchema(**model.model_dump())
    
    async def add_amount(self, user_id: int, amount: int):
        stmt = select(BalanceModel).where(BalanceModel.user_id == user_id)
        model = await self.get_one(stmt)

        if not model:
            model = BalanceModel(user_id=user_id, amount=amount)
            await self.add_one(model)
        else:
            model.amount += amount

        await self.session.commit()
        await self.session.refresh(model)

    async def remove_amount(self, user_id: int, amount: int):
        stmt = select(BalanceModel).where(BalanceModel.user_id == user_id)
        model = await self.get_one(stmt)

        if not model:
            raise BalanceNotFoundError("Unable to remove funds")
        
        model.amount -= amount
        if model.amount < 0:
            raise InsufficientFundsError("Insufficient balance")

        await self.session.commit()
        await self.session.refresh(model)
