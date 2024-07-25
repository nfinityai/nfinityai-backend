from fastapi import APIRouter, Depends

from backend_api.schemas.categories import (
    Category as CategorySchema,
)
from backend_api.schemas.categories import (
    CategoryList as CategorySchemaList,
)
from backend_api.schemas.models import (
    Model as ModelSchema,
)
from backend_api.schemas.models import (
    ModelList as ModelSchemaList,
)
from backend_api.services.auth import get_current_user
from backend_api.services.categories import CategoryService, get_category_service
from backend_api.services.models import ModelService, get_model_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/categories", response_model=CategorySchemaList)
async def get_categories(
    category_service: CategoryService = Depends(get_category_service),
):
    return await category_service.list_all_categories()


@router.get("/categories/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
):
    return await category_service.get_category(category_id)


@router.get("/models", response_model=ModelSchemaList)
async def get_models(
    category_id: int,
    model_service: ModelService = Depends(get_model_service),
):
    return await model_service.get_models_by_category(category_id)


@router.get("/models/{model_id}", response_model=ModelSchema)
async def get_model(
    model_id: int,
    model_service: ModelService = Depends(get_model_service),
):
    return await model_service.get_model(model_id)
