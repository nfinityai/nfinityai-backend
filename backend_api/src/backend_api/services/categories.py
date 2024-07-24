import logging

from fastapi import Depends
from sqlmodel import select
from typing_extensions import Annotated

from backend_api.backend.session import AsyncSession, get_session
from backend_api.models.categories import Category
from backend_api.schemas.categories import (
    Category as CategorySchema,
)
from backend_api.schemas.categories import (
    CreateCategory as CreateCategorySchema,
    CategoryList as CategoryListSchema
)
from backend_api.services.base import BaseDataManager, BaseService

logger = logging.getLogger(__name__)


class CategoryService(BaseService[Category]):
    async def get_category(self, category_id: int) -> CategorySchema:
        return await CategoryManager(self.session).get_category(category_id)

    async def get_category_by_slug(self, category_slug: str) -> CategorySchema | None:
        return await CategoryManager(self.session).get_category_by_slug(category_slug)

    async def add_category(self, category: CreateCategorySchema) -> CategorySchema:
        return await CategoryManager(self.session).add_category(category)

    async def list_categories(self) -> CategoryListSchema:
        categories = await CategoryManager(self.session).list_active_categories()
        return CategoryListSchema(categories=categories)


class CategoryManager(BaseDataManager[Category]):
    async def get_category(self, category_id: int) -> CategorySchema:
        stmt = select(Category).where(Category.id == category_id)

        model = await self.get_one(stmt)
        return CategorySchema(**model.model_dump())

    async def get_category_by_slug(self, category_slug: str) -> CategorySchema | None:
        stmt = select(Category).where(Category.slug == category_slug)

        model = await self.get_one(stmt)
        return CategorySchema(**model.model_dump()) if model else None

    async def list_active_categories(self) -> list[CategorySchema]:
        stmt = select(Category).where(Category.is_active)

        models = await self.get_all(stmt)
        return [CategorySchema(**model.model_dump()) for model in models]

    async def add_category(self, category: CreateCategorySchema) -> CategorySchema:
        model = await self.add_one(Category(**category.model_dump()))

        return CategorySchema(**model.model_dump())


async def get_category_service(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return CategoryService(session)
