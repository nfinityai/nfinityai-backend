from typing import Annotated

from fastapi import APIRouter, Depends

from backend_api.schemas.auth import SiweAuthModel, TokenModel, VerifyModel
from backend_api.schemas.users import CreateUser as CreateUserSchema
from backend_api.services.auth import AuthService, get_auth_service
from backend_api.utils import create_siwe_message, verify_siwe_message

router = APIRouter()


@router.get("/message", response_model=SiweAuthModel)
async def create_message(wallet_address: str):
    msg = create_siwe_message(wallet_address)
    return SiweAuthModel(message=msg)


@router.post("/verify", response_model=TokenModel)
async def verify_message(
    verify: Annotated[VerifyModel, Depends(verify_siwe_message)],
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_or_add_user(CreateUserSchema(wallet_address=verify.address))

    return await auth_service.authenticate(user.wallet_address)
