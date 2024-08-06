import logging

from fastapi import Depends
from sqlmodel import select, update
from typing_extensions import Annotated

from backend_api.backend.session import AsyncSession, get_session
from backend_api.schemas.models import (
    Model as ModelSchema,
    ModelList as ModelListSchema,
    CreateModel as CreateModelSchema,
    UpdateModel as UpdateModelSchema,
)
from backend_api.services.base import BaseDataManager, BaseService

logger = logging.getLogger(__name__)


class ModelService(BaseService[ModelSchema]):
    async def get_model(self, model_id: int) -> ModelSchema | None:
        return await ModelManager(self.session).get_model(model_id)

    async def get_model_by_slug(self, model_slug: str) -> ModelSchema | None:
        return await ModelManager(self.session).get_model_by_slug(model_slug)

    async def get_models_by_category(self, category_id: int) -> ModelListSchema:
        models = await ModelManager(self.session).get_models_by_category(category_id)
        return ModelListSchema(models=models)

    async def create_model(self, model: CreateModelSchema) -> ModelSchema:
        return await ModelManager(self.session).add_model(model)

    async def update_model(self, model: UpdateModelSchema) -> ModelSchema:
        return await ModelManager(self.session).upd_model(model)

    async def update_models_status(self, models_ids: list[int], status: bool) -> list[ModelSchema]:
        return await ModelManager(self.session).update_is_active(models_ids, status)


class ModelManager(BaseDataManager[ModelSchema]):
    async def get_model(self, model_id: int) -> ModelSchema | None:
        from backend_api.models.models import Model
        stmt = select(Model).where(Model.id == model_id)

        model = await self.get_one(stmt)
        return ModelSchema(**model.model_dump()) if model else None

    async def get_model_by_slug(self, model_slug: str) -> ModelSchema | None:
        from backend_api.models.models import Model
        stmt = select(Model).where(Model.slug == model_slug)

        model = await self.get_one(stmt)
        return ModelSchema(**model.model_dump()) if model else None

    async def get_active_model(self, model_id: int) -> ModelSchema | None:
        from backend_api.models.models import Model
        stmt = select(Model).where(Model.id == model_id, Model.is_active)

        model = await self.get_one(stmt)
        return ModelSchema(**model.model_dump()) if model else None

    async def get_models_by_category(self, category_id: int) -> list[ModelSchema]:
        from backend_api.models.models import Model
        stmt = select(Model).where(Model.category_id == category_id, Model.is_active)

        models = await self.get_all(stmt)
        return [ModelSchema(**model.model_dump()) for model in models]

    async def add_model(self, create_model: CreateModelSchema) -> ModelSchema:
        from backend_api.models.models import Model
        model = await self.add_one(Model(**create_model.model_dump()))
        return ModelSchema(**model.model_dump())

    async def upd_model(self, update_model: UpdateModelSchema) -> ModelSchema:
        from backend_api.models.models import Model
        stmt = select(Model).where(Model.id == update_model.id)
        model = await self.get_one(stmt)

        # Update model attributes
        for key, value in update_model.model_dump().items():
            setattr(model, key, value)

        await self.session.commit()
        await self.session.refresh(model)

        return ModelSchema(**model.model_dump())

    async def update_is_active(self, model_ids: list[int], status: bool) -> list[ModelSchema]:
        from backend_api.models.models import Model
        model_ids = list(map(int, model_ids))

        stmt = update(Model).where(Model.id.in_(model_ids)).values(is_active=status)
        await self.session.execute(stmt)
        await self.session.commit()

        stmt = select(Model).where(Model.id.in_(model_ids))
        models = await self.get_all(stmt)
        return [ModelSchema(**model.model_dump()) for model in models]


async def get_model_service(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return ModelService(session)
