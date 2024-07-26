from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ModelRunQuery(BaseModel):
    input: dict


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
    image_url: str | None = Field(..., validation_alias="cover_image_url")
    default_example: ModelProviderDefaultExampleModel
    latest_version: dict | None
    slug: str
    version: str | None


class ModelProviderModelList(BaseModel):
    models: list[ModelProviderModel]


class ModelProviderModelRunResultModel(BaseModel):
    error: str | None
    output: Any | None
    elapsed_time: float | None


class ModelProviderModelRunResult(BaseModel):
    result: ModelProviderModelRunResultModel


class ModelProviderModelRunAsync(BaseModel):
    id: str
    status: str
    created_at: datetime | None


class ModelProviderModelRunAsyncStatus(ModelProviderModelRunAsync):
    pass


class ModelProviderModelRunAsyncResult(ModelProviderModelRunAsync):
    result: ModelProviderModelRunResultModel
    finished_at: datetime | None


class ModelProviderHardwareCostInfo(BaseModel):
    name: str
    sku: str
    price_per_second: float
    price_per_hour: float
    gpu_count: int
    cpu_count: int
    gpu_ram_gb: int
    ram_gb: int


class ModelProviderHardwareCosts(BaseModel):
    info: list[ModelProviderHardwareCostInfo]


class ModelProviderModelCostInfo(BaseModel):
    name: str
    sku: str
    prediction_time: float


class ModelProviderModelCosts(BaseModel):
    info: ModelProviderModelCostInfo
