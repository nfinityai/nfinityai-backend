from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    slug: str
    description: str


class CategoryList(BaseModel):
    categories: list[Category]


class CreateCategory(BaseModel):
    name: str
    slug: str
    description: str
