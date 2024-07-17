from fastapi import APIRouter
from .endpoints import base

api_router = APIRouter()
api_router.include_router(
    base.router, tags=["Endpoints"]
)
