from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, Column


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

    class Config:
        arbitrary_types_allowed = True
