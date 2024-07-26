from fastapi import Depends
from typing_extensions import Annotated
from sqlmodel import select

from backend_api.backend.session import AsyncSession, get_session
from backend_api.models.users import User as UserModel
from backend_api.schemas.users import User as UserSchema

from .base import BaseDataManager, BaseService


class UserService(BaseService[UserModel]):
    async def get_user_by_id(self, user_id: int) -> UserSchema:
        return await UserDataManager(self.session).get_user_by_id(user_id)

    async def get_user(self, address: str) -> UserSchema:
        return await UserDataManager(self.session).get_user(address)


class UserDataManager(BaseDataManager[UserModel]):
    async def get_user_by_id(self, user_id: int) -> UserSchema:
        stmt = select(UserModel).where(UserModel.id == user_id)

        model = await self.get_one(stmt)
        return UserSchema(**model.model_dump())


    async def get_user(self, address: str) -> UserSchema:
        stmt = select(UserModel).where(UserModel.wallet_address == address)

        model = await self.get_one(stmt)
        return UserSchema(**model.model_dump())



async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)
