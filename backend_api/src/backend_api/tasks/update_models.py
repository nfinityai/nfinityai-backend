from datetime import datetime
from backend_api.backend.config import get_settings
from backend_api.backend.session import get_session
from backend_api.backend.tasks import scheduler
from backend_api.schemas.categories import CategoryList as CategoryListSchema
from backend_api.schemas.model_providers import ModelProviderModelList
from backend_api.schemas.models import (
    CreateModel as CreateModelSchema,
)
from backend_api.schemas.models import (
    UpdateModel as UpdateModelSchema,
)
from backend_api.services.categories import CategoryService, get_category_service
from backend_api.services.model_providers import ModelProviderService
from backend_api.services.models import ModelService, get_model_service


async def _get_categories() -> CategoryListSchema:
    async for session in get_session():
        service: CategoryService = await get_category_service(session)

        return await service.list_categories()
    return CategoryListSchema(categories=[])


async def _get_models(category_slug: str) -> ModelProviderModelList:
    settings = get_settings()
    async with ModelProviderService(settings) as service:
        return await service.list_models(settings.provider, category_slug)


@scheduler.scheduled_job("interval", days=1, next_run_time=datetime.now())
async def update_models():
    categories = (await _get_categories()).categories
    async for session in get_session():
        service: ModelService = await get_model_service(session)
        for category in categories:
            for model in (await _get_models(category.slug)).models:
                existed = await service.get_model_by_slug(model.slug)
                if existed:
                    await service.update_model(
                        UpdateModelSchema(id=existed.id, **model.model_dump())
                    )
                    continue
                await service.create_model(CreateModelSchema(category_id=category.id, **model.model_dump()))
