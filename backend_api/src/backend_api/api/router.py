from fastapi import APIRouter

from backend_api.api.endpoints import auth, users, model_providers, balance, transactions, runs

api_router = APIRouter()
api_router.include_router(
    auth.router, prefix="/auth", tags=["SIWE Authentication Endpoints"]
)
api_router.include_router(users.router, prefix="/user", tags=["User Endpoints"])
api_router.include_router(balance.router, prefix="/user", tags=["User Endpoints"])
api_router.include_router(transactions.router, prefix="/user", tags=["User Endpoints"])
api_router.include_router(runs.router, prefix="/runs", tags=["Run Endpoints"])
api_router.include_router(model_providers.router, tags=["Provider Endpoints"])
