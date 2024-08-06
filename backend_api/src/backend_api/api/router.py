from fastapi import APIRouter

from backend_api.api.endpoints import auth, models, users, balance, transactions, runs, media

api_router = APIRouter()
api_router.include_router(
    auth.router, prefix="/auth", tags=["SIWE Authentication Endpoints"]
)
api_router.include_router(users.router, prefix="/user", tags=["User Endpoints"])
api_router.include_router(balance.router, prefix="/user", tags=["User Endpoints"])
api_router.include_router(transactions.router, prefix="/user", tags=["User Endpoints"])
api_router.include_router(models.router, tags=["Models Endpoints"])
api_router.include_router(runs.router, prefix="/runs", tags=["Run Endpoints"])

api_router.include_router(media.router, prefix="/media", tags=["Media Endpoints"])