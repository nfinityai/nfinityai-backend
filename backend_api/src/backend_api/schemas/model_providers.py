from typing import Any
from pydantic import BaseModel, Field


class ModelProviderCategory(BaseModel):
    name: str
    slug: str
    description: str
    provider: str = Field(exclude=True)


class ModelProviderCategoryList(BaseModel):
    categories: list[ModelProviderCategory]


class ModelProviderDefaultExampleModel(BaseModel):
    input: dict | None
    output: Any


class ModelProviderModel(BaseModel):
    name: str
    description: str
    run_count: int
    image_url: str = Field(validation_alias='cover_image_url')
    default_example: ModelProviderDefaultExampleModel
    latest_version: dict
    slug: str
    version: str


class ModelProviderModelList(BaseModel):
    models: list[ModelProviderModel]


class ModelProviderModelRunResult(BaseModel):
    result: dict
