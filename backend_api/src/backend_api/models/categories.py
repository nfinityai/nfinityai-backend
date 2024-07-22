from datetime import datetime
from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    slug: str = Field(nullable=False)
    description: str = Field(nullable=True)
    is_active: bool = Field(default=False, nullable=False)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
