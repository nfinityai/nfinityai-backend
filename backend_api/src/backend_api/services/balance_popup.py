from fastapi import Depends
from sqlmodel import select
from typing_extensions import Annotated

from backend_api.backend.session import AsyncSession, get_session
from backend_api.models.balance import BalancePopup as BalancePopupModel
from backend_api.schemas.balance import BalancePopupModel as BalancePopupSchema
from backend_api.schemas.balance import CreateBalancePopupModel as CreateBalancePopupSchema, UpdateBalancePopupModel as UpdateBalancePopupSchema

from .base import BaseDataManager, BaseService


class BalancePopupService(BaseService[BalancePopupModel]):
    async def get_balance_popup(self, id: int) -> BalancePopupSchema | None:
        return await BalancePopupDataManager(self.session).get_balance_popup(id)

    async def create_balance_popup(self, balance: CreateBalancePopupSchema) -> BalancePopupSchema:
        return await BalancePopupDataManager(self.session).add_balance_popup(balance)

    async def update_balance_popup(self, balance: UpdateBalancePopupSchema) -> BalancePopupSchema:
        return await BalancePopupDataManager(self.session).upd_balance_popup(balance)
    
    async def get_unfinished_balance_popups(self) -> list[BalancePopupSchema]:
        return await BalancePopupDataManager(self.session).get_unfinished_balance_popups()


class BalancePopupDataManager(BaseDataManager[BalancePopupModel]):
    async def get_unfinished_balance_popups(self) -> list[BalancePopupSchema]:
        stmt = select(BalancePopupModel).where(BalancePopupModel.finished_at is None)
        models = await self.get_all(stmt)
        return [BalancePopupSchema(**model.model_dump()) for model in models]

    async def get_balance_popup(self, id: int) -> BalancePopupSchema | None:
        stmt = select(BalancePopupModel).where(BalancePopupModel.id == id)

        model = await self.get_one(stmt)
        return BalancePopupSchema(**model.model_dump()) if model is not None else None

    async def add_balance_popup(self, balance_popup: CreateBalancePopupSchema) -> BalancePopupSchema:
        model = await self.add_one(BalancePopupModel(**balance_popup.model_dump()))

        return BalancePopupSchema(**model.model_dump())

    async def upd_balance_popup(self, balance_popup: UpdateBalancePopupSchema) -> BalancePopupSchema:
        model = await self.add_one(BalancePopupModel(**balance_popup.model_dump()))

        return BalancePopupSchema(**model.model_dump())


async def get_balance_popup_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BalancePopupService:
    return BalancePopupService(session)
