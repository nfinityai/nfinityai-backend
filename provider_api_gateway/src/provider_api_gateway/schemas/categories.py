from pydantic import BaseModel, ConfigDict
from .types import ProviderEnum


class ProviderModelCategory(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: str
    description: str | None = None
    provider: ProviderEnum
    slug: str


    @classmethod
    def from_provider_model(cls, provider: ProviderEnum, model: BaseModel) -> "ProviderModelCategory":
        return cls(provider=provider, **model.dict() if hasattr(model, "dict") else model.model_dump())



class ProviderModelCategoriesList(BaseModel):
    categories: list[ProviderModelCategory]
