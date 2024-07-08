from fastapi import APIRouter
from .endpoints import replicate

api_router = APIRouter()
api_router.include_router(
    replicate.router, prefix="/replicate", tags=["Replicate Endpoints"]
)
