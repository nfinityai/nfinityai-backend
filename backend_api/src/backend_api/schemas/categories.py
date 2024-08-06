from pydantic import BaseModel

from backend_api.schemas.media import FileInfo


class Category(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    is_active: bool

    icon_svg: FileInfo | None = None


class CategoryList(BaseModel):
    categories: list[Category]


class CreateCategory(BaseModel):
    name: str
    slug: str
    description: str
