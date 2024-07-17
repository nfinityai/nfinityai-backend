from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from provider_api_gateway.api.endpoints import replicate
from provider_api_gateway.providers.replicate import (
    ReplicateClient,
    get_replicate_client,
)
from provider_api_gateway.schemas.categories import ProviderModelCategoriesList
from provider_api_gateway.schemas.types import ProviderEnum

router = APIRouter()


@router.get("/categories", response_model=ProviderModelCategoriesList)
async def list_categories(
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
):
    try:
        categories = await client.list_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ProviderModelCategoriesList(categories=categories)


router.include_router(
    replicate.router, prefix=f"/{ProviderEnum.REPLICATE}", tags=[f"{ProviderEnum.REPLICATE.capitalize()} Endpoints"]
)
