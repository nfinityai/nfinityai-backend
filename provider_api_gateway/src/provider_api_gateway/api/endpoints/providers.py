from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from provider_api_gateway.api.endpoints import replicate
from provider_api_gateway.providers.replicate import (
    ReplicateClient,
    get_replicate_client,
)
from provider_api_gateway.schemas.categories import ProviderModelCategoriesList
from provider_api_gateway.schemas.runs import RunResult, RunStatus
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


@router.get("/runs/{id}/status", response_model=RunStatus)
async def get_run_status(
    id: str,
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
):
    try:
        status = await client.get_run_model_status(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return status


@router.get("/runs/{id}/result", response_model=RunResult)
async def get_run_result(
    id: str,
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
):
    try:
        result = await client.get_run_model_result(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result


router.include_router(
    replicate.router, prefix=f"/{ProviderEnum.REPLICATE}", tags=[f"{ProviderEnum.REPLICATE.capitalize()} Endpoints"]
)
