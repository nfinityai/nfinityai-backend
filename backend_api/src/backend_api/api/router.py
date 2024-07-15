from fastapi import APIRouter

from backend_api.api.endpoints import auth, users

api_router = APIRouter()
api_router.include_router(
    auth.router, prefix="/auth", tags=["SIWE Authentication Endpoints"]
)
api_router.include_router(
    users.router, prefix="/users", tags=["User Endpoints"]
)
