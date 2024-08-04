from datetime import datetime
from fastapi import UploadFile
from sqlmodel import SQLModel, Field, Column
from starlette_admin.contrib.sqla import ModelView
from sqlalchemy_file import ImageField, File, FileField
from backend_api.admin import site


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

site.add_view(ModelView(Category))
