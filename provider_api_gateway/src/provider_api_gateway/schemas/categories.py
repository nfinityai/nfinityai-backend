from pydantic import BaseModel, ConfigDict
from .types import ProviderEnum


class Category(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    description: str | None = None
    provider: ProviderEnum
    slug: str


    @classmethod
    def from_provider_model(cls, provider: ProviderEnum, model: BaseModel) -> "Category":
        return cls(provider=provider, **model.model_dump())



class CategoriesList(BaseModel):
    categories: list[Category]
