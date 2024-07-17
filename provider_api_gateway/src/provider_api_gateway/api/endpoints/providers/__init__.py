from fastapi import APIRouter

from provider_api_gateway.api.endpoints.providers import replicate
from provider_api_gateway.schemas.types import ProviderEnum


router = APIRouter()

router.include_router(
    replicate.router, prefix=ProviderEnum.REPLICATE.as_prefix(), tags=[ProviderEnum.REPLICATE.as_tag()]
)
