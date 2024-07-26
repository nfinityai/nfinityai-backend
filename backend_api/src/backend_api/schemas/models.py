from typing import Any

from pydantic import BaseModel, Field
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
    latest_version: dict = {}
    slug: str
    version: str | None

    category_id: int

    created_at: datetime = Field(default_factory=datetime.now)


class UpdateModel(BaseModel):
    id: int
    name: str
    description: str
    image_url: str | None
    default_example: DefaultExampleModel
    latest_version: dict = {}
    version: str | None

    updated_at: datetime = Field(default_factory=datetime.now)


class ModelList(BaseModel):
    models: list[Model]
