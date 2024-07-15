from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing_extensions import Annotated

from provider_api_gateway.providers.replicate import (
    ReplicateClient,
    get_replicate_client,
)

router = APIRouter()


class RunModelQuery(BaseModel):
    input: dict


@router.get("/collections")
async def list_collections(
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
):
    try:
        collections = await client.list_collections()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return [collection.dict() for collection in collections]


@router.get("/collections/{collection}/models")
async def list_models(
    collection: str,
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
):
    try:
        models = await client.list_models(collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return models


@router.post("/run/{model:path}")
async def run_model(
    model: str,
    input: RunModelQuery,
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
):
    try:
        models = await client.run_model(model, input_params=input.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return models


