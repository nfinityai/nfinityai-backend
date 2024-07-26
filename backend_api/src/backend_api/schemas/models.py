from typing import Any

from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class DefaultExampleModel(BaseModel):
    input: dict | None
    output: Any


class Model(BaseModel):
    id: int
    name: str
    description: str
    run_count: int
    image_url: str | None
    default_example: DefaultExampleModel
    latest_version: dict
    slug: str
    version: str | None

    category_id: int


class CreateModel(BaseModel):
    name: str
    description: str
    run_count: int = 0
    image_url: str | None
    default_example: DefaultExampleModel
    latest_version: dict | None
    slug: str
    version: str | None

    category_id: int

    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("latest_version", mode="before")
    def set_latest_version(cls, value):
        return value or {}


class UpdateModel(BaseModel):
    id: int
    name: str
    description: str
    image_url: str | None
    default_example: DefaultExampleModel
    latest_version: dict | None
    slug: str
    version: str | None

    category_id: int

    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("latest_version", mode="before")
    def set_latest_version(cls, value):
        return value or {}


class ModelList(BaseModel):
    models: list[Model]
