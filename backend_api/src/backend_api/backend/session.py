from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession as _AsyncSession

from backend_api.backend.config import settings

engine = create_async_engine(settings.database_url, echo=True, future=True)


class AsyncSession(_AsyncSession):
    pass


async def get_session():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
    async with async_session() as session:  # type: ignore
        yield session
