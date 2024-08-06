import logging
from typing import List

from fastapi import Depends
from sqlmodel import select, update
from typing_extensions import Annotated

from backend_api.backend.session import AsyncSession, get_session
from backend_api.schemas.categories import (
    Category as CategorySchema,
)
from backend_api.schemas.categories import (
    CreateCategory as CreateCategorySchema,
    CategoryList as CategoryListSchema,
)
from backend_api.services.base import BaseDataManager, BaseService

logger = logging.getLogger(__name__)


class CategoryService(BaseService[CategorySchema]):
    async def get_category(self, category_id: int) -> CategorySchema | None:
        return await CategoryManager(self.session).get_category(category_id)

    async def get_category_by_slug(self, category_slug: str) -> CategorySchema | None:
        return await CategoryManager(self.session).get_category_by_slug(category_slug)

    async def add_category(self, category: CreateCategorySchema) -> CategorySchema:
        return await CategoryManager(self.session).add_category(category)

    async def list_categories(self) -> CategoryListSchema:
        categories = await CategoryManager(self.session).list_active_categories()
        return CategoryListSchema(categories=categories)

    async def list_all_categories(self) -> CategoryListSchema:
        categories = await CategoryManager(self.session).list_all_categories()
        return CategoryListSchema(categories=categories)

    async def update_categories_status(
        self, category_ids: List[int], status: bool
    ) -> List[CategorySchema]:
        return await CategoryManager(self.session).update_is_active(category_ids, status)


class CategoryManager(BaseDataManager[CategorySchema]):
    async def get_category(self, category_id: int) -> CategorySchema | None:
        from backend_api.models.categories import Category

        stmt = select(Category).where(Category.id == category_id)
        model = await self.get_one(stmt)
        return CategorySchema(**model.model_dump()) if model else None

    async def get_category_by_slug(self, category_slug: str) -> CategorySchema | None:
        from backend_api.models.categories import Category

        stmt = select(Category).where(Category.slug == category_slug)
        model = await self.get_one(stmt)
        return CategorySchema(**model.model_dump()) if model else None

    async def list_active_categories(self) -> List[CategorySchema]:
        from backend_api.models.categories import Category

        stmt = select(Category).where(Category.is_active)
        models = await self.get_all(stmt)
        return [CategorySchema(**model.model_dump()) for model in models]

    async def list_all_categories(self) -> List[CategorySchema]:
        from backend_api.models.categories import Category

        stmt = select(Category)
        models = await self.get_all(stmt)
        return [CategorySchema(**model.model_dump()) for model in models]

    async def add_category(self, category: CreateCategorySchema) -> CategorySchema:
        from backend_api.models.categories import Category

        model = await self.add_one(Category(**category.model_dump()))
        return CategorySchema(**model.model_dump())

    async def update_is_active(self, category_ids: List[int], status: bool) -> List[CategorySchema]:
        from backend_api.models.categories import Category

        category_ids = list(map(int, category_ids))

        stmt = update(Category).where(Category.id.in_(category_ids)).values(is_active=status)
        await self.session.execute(stmt)
        await self.session.commit()

        stmt = select(Category).where(Category.id.in_(category_ids))
        categories = await self.get_all(stmt)
        return [CategorySchema(**category.model_dump()) for category in categories]


async def get_category_service(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return CategoryService(session)
