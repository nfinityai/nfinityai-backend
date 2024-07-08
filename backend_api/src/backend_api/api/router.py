from fastapi import APIRouter

from backend_api.api.endpoints import auth, configurations, gpus, rental, users

api_router = APIRouter()
api_router.include_router(
    auth.router, prefix="/auth", tags=["SIWE Authentication Endpoints"]
)
api_router.include_router(
    users.router, prefix="/users", tags=["User Endpoints"]
)
api_router.include_router(
    gpus.router, prefix="/gpus", tags=["GPU Endpoints"]
)
api_router.include_router(
    configurations.router, prefix="/configurations", tags=["Configuration Endpoints"]
)
api_router.include_router(
    rental.router, prefix="/rental", tags=["Rental Endpoints"]
)
