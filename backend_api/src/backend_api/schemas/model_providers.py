from pydantic import BaseModel


class ModelProviderCategory(BaseModel):
    name: str
    slug: str
    description: str


class ModelProviderCategoryList(BaseModel):
    categories: list[ModelProviderCategory]


class ModelProviderModel(BaseModel):
    owner: str
    name: str
    description: str
    default_example: dict
    latest_version: dict


class ModelProviderModelList(BaseModel):
    models: list[ModelProviderModel]


class ModelProviderModelRunResult(BaseModel):
    result: dict
