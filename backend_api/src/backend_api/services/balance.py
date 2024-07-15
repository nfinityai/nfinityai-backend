from sqlmodel import select

from backend_api.exceptions import BalanceNotFoundError, InsufficientFundsError
from backend_api.models.balance import Credit as CreditModel
from backend_api.schemas.balance import Credit as CreditSchema

from .base import BaseDataManager, BaseService


class CreditService(BaseService[CreditModel]):
    async def get_balance(self, address: str) -> CreditSchema:
        return await CreditDataManager(self.session).get_balance(address)


class CreditDataManager(BaseDataManager[CreditModel]):
    async def get_balance(self, address: str) -> CreditSchema:
        stmt = select(CreditModel).where(CreditModel.user_id == address)

        model = await self.get_one(stmt)
        return CreditSchema(**model.model_dump())
    
    async def add_credits(self, address: str, amount: int):
        stmt = select(CreditModel).where(CreditModel.user_id == address)
        model = await self.get_one(stmt)

        if not model:
            model = CreditModel(user_id=address, balance=amount)
            await self.add_one(model)
        else:
            model.balance += amount

        await self.session.commit()
        await self.session.refresh(model)

    async def remove_credits(self, address: str, amount: int):
        stmt = select(CreditModel).where(CreditModel.user_id == address)
        model = await self.get_one(stmt)

        if not model:
            raise BalanceNotFoundError("Unable to remove funds")
        
        model.balance -= amount
        if model.balance < 0:
            raise InsufficientFundsError("Insufficient balance")

        await self.session.commit()
        await self.session.refresh(model)
