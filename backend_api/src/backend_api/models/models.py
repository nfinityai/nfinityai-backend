from datetime import datetime

from fastapi import Request
from sqlmodel import SQLModel, Field, JSON, Column, Relationship
from starlette_admin import HasOne, action
from starlette_admin.contrib.sqla import ModelView
from backend_api.admin import site
from backend_api.backend.session import get_session
from backend_api.models import Category
from backend_api.services.models import ModelService, get_model_service


class Model(SQLModel, table=True):
    __tablename__ = "models"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    category_id: int = Field(default=None, foreign_key="categories.id")
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False)
    default_example: dict = Field(default_factory=dict, sa_column=Column(JSON))
    latest_version: dict = Field(default_factory=dict, sa_column=Column(JSON))
    version: str = Field(nullable=True)
    description: str = Field(nullable=True)
    run_count: int = Field(default=0)
    image_url: str = Field(nullable=True)
    is_active: bool = Field(default=False, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    category: Category = Relationship()

    class Config:
        arbitrary_types_allowed = True


class ModelAdminView(ModelView):
    model = Model
    fields = [
        "id",
        HasOne("category", identity="category"),
        "is_active",
        "name",
        "slug",
        "default_example",
        "latest_version",
        "version",
        "description",
        "run_count",
        "image_url",
        "created_at",
        "updated_at",
    ]
    actions = [
        "activate_models",
        "deactivate_models",
    ]

    @action(
        name="activate_models",
        text="Activate Models",
        confirmation="Are you sure you want to activate selected models?",
    )
    async def activate_models(
        self,
        request: Request,
        pks: list[int],
    ) -> str:
        async for session in get_session():
            service: ModelService = await get_model_service(session)
            await service.update_models_status(pks, status=True)
        return "Selected models have been activated."

    @action(
        name="deactivate_models",
        text="Deactivate Models",
        confirmation="Are you sure you want to activate selected models?",
    )
    async def deactivate_models(self, request: Request, pks: list[int]) -> str:
        async for session in get_session():
            service: ModelService = await get_model_service(session)
            await service.update_models_status(pks, status=False)
        return "Selected models have been deactivated."


site.add_view(ModelAdminView(Model))
