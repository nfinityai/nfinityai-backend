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


@router.get("/categories/{category}/models")
async def list_models(
    category: str,
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
):
    try:
        models = await client.list_models(category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return models


@router.post("/models/{model}/run")
async def run_model(
    model: str,
    run_query: RunModelQuery,
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
    version: str | None = None,
):
    try:
        models = await client.run_model(model, version, input_params=run_query.input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return models


@router.post("/models/{model}/run_async")
async def run_model_async(
    model: str,
    run_query: RunModelQuery,
    client: Annotated[ReplicateClient, Depends(get_replicate_client)],
    version: str | None = None,
):
    try:
        models = await client.run_model_async(
            model, version, input_params=run_query.input
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return models
