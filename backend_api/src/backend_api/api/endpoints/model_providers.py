from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend_api.backend.config import Settings, get_settings
from backend_api.schemas.model_providers import (
    ModelProviderCategoryList as ModelProviderCategorySchemaList,
    ModelProviderModelRunAsync,
)
from backend_api.schemas.model_providers import (
    ModelProviderModelList as ModelProviderModelSchemaList,
)
from backend_api.schemas.model_providers import (
    ModelProviderModelRunResult as ModelProviderModelRunResultSchema,
)
from backend_api.services.auth import get_current_user
from backend_api.services.model_providers import (
    ModelProviderService,
    get_model_provider_service,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


class ModelRunQuery(BaseModel):
    input: dict


@router.get("/categories", response_model=ModelProviderCategorySchemaList)
async def get_all_categories(
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
):
    return await model_provider_service.list_categories()


@router.get(
    "/categories/{category}/models", response_model=ModelProviderModelSchemaList
)
async def get_all_models(
    category: str,
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
):
    return await model_provider_service.list_models(settings.provider, category)


@router.post("/models/{model}/run", response_model=ModelProviderModelRunResultSchema)
async def run_model(
    model: str,
    run_query: ModelRunQuery,
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
    version: str | None = None,
):
    return await model_provider_service.run_model(
        settings.provider, model, run_query.input, version
    )


@router.post("/models/{model}/run_async", response_model=ModelProviderModelRunAsync)
async def run_model_async(
    model: str,
    run_query: ModelRunQuery,
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
    version: str | None = None,
):
    return await model_provider_service.run_model_async(
        settings.provider, model, run_query.input, version
    )


@router.post("/run/{id}/status", response_model=ModelProviderModelRunAsync)
async def run_model_status(
    model: str,
    run_query: ModelRunQuery,
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
    version: str | None = None,
):
    return await model_provider_service.run_model_async(
        settings.provider, model, run_query.input, version
    )
