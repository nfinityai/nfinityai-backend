from fastapi import APIRouter
from .endpoints import providers

api_router = APIRouter()
api_router.include_router(
    providers.router, prefix="/providers", tags=["Providers Endpoints"]
)
