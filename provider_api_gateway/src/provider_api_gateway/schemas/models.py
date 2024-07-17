from typing import Any

from pydantic import BaseModel, Field, computed_field

from provider_api_gateway.services.extractors.replicate import (
    CostInfoModel,
)
from provider_api_gateway.utils import encode_string


class ProviderModelDefaultExampleModel(BaseModel):
    input: dict | None
    output: Any | None


class ProviderModel(BaseModel):
    owner: str = Field(..., exclude=True)
    """
    The owner of the model.
    """

    name: str
    """
    The name of the model.
    """

    description: str | None
    """
    The description of the model.
    """

    run_count: int
    """
    The number of runs of the model.
    """

    cover_image_url: str | None
    """
    The URL of the cover image for the model.
    """

    default_example: ProviderModelDefaultExampleModel | None
    """
    The default example of the model.
    """

    latest_version: dict | None
    """
    The latest version of the model.
    """

    @computed_field
    @property
    def slug(self) -> str:
        slug = f"{self.owner}/{self.name}"
        return encode_string(slug)

    @computed_field
    @property
    def version(self) -> str | None:
        if self.latest_version is not None and "id" in self.latest_version:
            return self.latest_version["id"]
        return None


class ProviderModelList(BaseModel):
    models: list[ProviderModel]


class ProviderModelCost(BaseModel):
    info: CostInfoModel | None


class ProviderHardwareCost(BaseModel):
    info: Any | None