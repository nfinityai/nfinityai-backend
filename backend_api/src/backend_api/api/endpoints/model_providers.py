from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing_extensions import Annotated

from backend_api.backend.config import Settings, get_settings
from backend_api.schemas.model_providers import (
    ModelProviderCategoryList as ModelProviderCategorySchemaList,
)
from backend_api.schemas.model_providers import (
    ModelProviderModelList as ModelProviderModelSchemaList,
)
from backend_api.schemas.model_providers import (
    ModelProviderModelRunResult as ModelProviderModelRunResultSchema,
)
from backend_api.schemas.users import User as UserModel
from backend_api.services.auth import get_current_user
from backend_api.services.model_providers import (
    ModelProviderService,
    get_model_provider_service,
)

router = APIRouter()


class ModelRunQuery(BaseModel):
    input: dict


@router.get("/categories", response_model=ModelProviderCategorySchemaList)
async def get_all_categories(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
):
    return ModelProviderCategorySchemaList(
        categories=await model_provider_service.list_categories()
    )


@router.get(
    "/categories/{category}/models", response_model=ModelProviderModelSchemaList
)
async def get_all_models(
    category: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
):
    return ModelProviderModelSchemaList(
        models=await model_provider_service.list_models(settings.provider, category)
    )


@router.get("/models/run/{model}", response_model=ModelProviderModelRunResultSchema)
async def run_model(
    model: str,
    run_query: ModelRunQuery,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    model_provider_service: ModelProviderService = Depends(get_model_provider_service),
    settings: Settings = Depends(get_settings),
    version: str | None = None,
):
    return ModelProviderModelRunResultSchema(
        result=await model_provider_service.run_model(settings.provider, model, run_query.input, version)
    )
