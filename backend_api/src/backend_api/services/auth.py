from typing_extensions import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import select

from backend_api.backend.config import Settings, get_settings
from backend_api.backend.session import AsyncSession, get_session
from backend_api.models.users import User as UserModel
from backend_api.schemas.auth import PayloadModel, TokenModel
from backend_api.schemas.users import User as UserSchema, UserModel as UserModelSchema, CreateUser as CreateUserSchema
from backend_api.services.users import UserService, get_user_service
from backend_api.utils import create_jwt, decode_jwt

from .base import BaseDataManager, BaseService


class JWTBearer(HTTPBearer):
    pass


auth_schema = JWTBearer()


class AuthService(BaseService[UserModel]):
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        super().__init__(session)
        self.settings = settings

    async def get_or_add_user(self, user: CreateUserSchema) -> UserSchema:
        user_model = UserModel(**user.model_dump())
        return await AuthDatamanager(self.session).get_or_add_user(user_model)

    async def create_user(self, user: CreateUserSchema) -> None:
        user_model = UserModel(**user.model_dump())
        await AuthDatamanager(self.session).add_user(user_model)

    async def authenticate(self, address: str):
        user = await AuthDatamanager(self.session).get_user(address)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        payload = PayloadModel(address=address)
        access_token = create_jwt(payload.model_dump(), self.settings)

        return TokenModel(access_token=access_token)


class AuthDatamanager(BaseDataManager[UserModel]):
    async def add_user(self, user: UserModel) -> None:
        await self.add_one(user)

    async def get_user(self, address: str) -> UserSchema | None:
        stmt = select(UserModel).where(UserModel.wallet_address == address)

        model = await self.get_one(stmt)
        return UserSchema(**model.model_dump()) if model is not None else None

    async def get_or_add_user(self, user: UserModel) -> UserSchema:
        user_model = await self.get_user(user.wallet_address)

        if user_model is None:
            await self.add_user(user)
            return UserSchema(**user.model_dump())

        return user_model


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(auth_schema)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserSchema | None:
    if credentials is None or credentials.credentials is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    payload = decode_jwt(credentials.credentials, settings=get_settings())

    return await user_service.get_user(UserModelSchema(**payload).address)


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    return AuthService(session, settings)
