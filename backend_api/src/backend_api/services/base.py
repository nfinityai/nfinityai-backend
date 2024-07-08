from typing import (
    Generic,
    List,
    Sequence,
    TypeVar,
)

from sqlalchemy.sql.expression import Executable

from backend_api.backend.session import AsyncSession


class SessionMixin:
    """Provides instance of database session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session


T = TypeVar("T")


class BaseService(SessionMixin, Generic[T]):
    """Base class for application services."""

    pass


class BaseDataManager(SessionMixin, Generic[T]):
    """Base data manager class responsible for operations over database."""

    async def add_one(self, model: T) -> T:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def add_all(self, models: Sequence[T]) -> None:
        self.session.add_all(models)

    async def get_one(self, select_stmt: Executable) -> T:
        return await self.session.scalar(select_stmt)

    async def get_all(self, select_stmt: Executable) -> List[T]:
        return list((await self.session.scalars(select_stmt)).all())
