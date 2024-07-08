
from fastapi import APIRouter, Depends

from backend_api.schemas.users import UserModel
from backend_api.services.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserModel)
async def get_user_me(current_user: UserModel = Depends(get_current_user)):
    return UserModel(**current_user.model_dump())
