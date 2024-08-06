from datetime import datetime
from fastapi import UploadFile, Request
from sqlmodel import SQLModel, Field, Column
from starlette_admin import action
from starlette_admin.contrib.sqla import ModelView
from sqlalchemy_file import File, FileField
from backend_api.admin import site
from backend_api.backend.session import get_session
from backend_api.services.categories import CategoryService, get_category_service


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False)
    description: str = Field(nullable=True)
    is_active: bool = Field(default=False, nullable=False)
    icon_svg: File | UploadFile | None = Field(default=None, sa_column=Column(FileField(upload_storage='category_icons')))  # type: ignore

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

    class Config:
        arbitrary_types_allowed = True


class CategoryAdminView(ModelView):
    model = Category
    actions = [
        "activate_categories",
        "deactivate_categories",
    ]

    @action(
        name="activate_categories",
        text="Activate Categories",
        confirmation="Are you sure you want to activate selected categories?",
    )
    async def activate_categories(
        self,
        request: Request,
        pks: list[int],
    ) -> str:
        async for session in get_session():
            service: CategoryService = await get_category_service(session)
            await service.update_categories_status(pks, status=True)
        return "Selected categories have been activated."

    @action(
        name="deactivate_categories",
        text="Deactivate Categories",
        confirmation="Are you sure you want to deactivate selected categories?",
    )
    async def deactivate_categories(self, request: Request, pks: list[int]) -> str:
        async for session in get_session():
            service: CategoryService = await get_category_service(session)
            await service.update_categories_status(pks, status=False)
        return "Selected categories have been deactivated."


site.add_view(CategoryAdminView(Category))
