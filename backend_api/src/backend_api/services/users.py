from sqlmodel import select

from backend_api.models.users import User as UserModel
from backend_api.schemas.users import User as UserSchema

from .base import BaseDataManager, BaseService


class UserService(BaseService[UserModel]):
    async def get_user(self, address: str) -> UserSchema:
        return await UserDataManager(self.session).get_user(address)


class UserDataManager(BaseDataManager[UserModel]):
    async def get_user(self, address: str) -> UserSchema:
        stmt = select(UserModel).where(UserModel.address == address)

        model = await self.get_one(stmt)
        return UserSchema(**model.model_dump())
