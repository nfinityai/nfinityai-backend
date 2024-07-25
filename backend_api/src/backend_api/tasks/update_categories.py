from datetime import datetime
from backend_api.backend.session import get_session
from backend_api.backend.tasks import scheduler
from backend_api.schemas.categories import CreateCategory
from backend_api.schemas.model_providers import ModelProviderCategoryList
from backend_api.services.categories import CategoryService, get_category_service
from backend_api.services.model_providers import ModelProviderService
from backend_api.backend.config import get_settings


async def _get_categories() -> ModelProviderCategoryList:
    settings = get_settings()
    async with ModelProviderService(settings) as service:
        return await service.list_categories()


@scheduler.scheduled_job('interval', weeks=1, next_run_time=datetime.now())
async def update_categories():
    async for session in get_session():
        service: CategoryService = await get_category_service(session)
        for category in (await _get_categories()).categories:
            exists = await service.get_category_by_slug(category.slug)
            if exists:
                continue
            await service.add_category(CreateCategory(**category.model_dump()))
