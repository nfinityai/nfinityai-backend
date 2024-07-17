from pydantic import BaseModel


class ModelProviderCategory(BaseModel):
    name: str
    slug: str
    description: str
    provider: str


class ModelProviderCategoryList(BaseModel):
    categories: list[ModelProviderCategory]


class ModelProviderDefaultExampleModel(BaseModel):
    input: dict
    output: dict


class ModelProviderModel(BaseModel):
    name: str
    description: str
    run_count: int
    image_url: str
    default_example: ModelProviderDefaultExampleModel
    latest_version: dict
    slug: str
    version: str


class ModelProviderModelList(BaseModel):
    models: list[ModelProviderModel]


class ModelProviderModelRunResult(BaseModel):
    result: dict
