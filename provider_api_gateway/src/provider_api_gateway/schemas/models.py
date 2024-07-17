from typing import Any
from pydantic import BaseModel

from provider_api_gateway.utils import encode_string


class ProviderModel(BaseModel):
    owner: str
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

    default_example: dict | None
    """
    The default example of the model.
    """

    latest_version: dict | None
    """
    The latest version of the model.
    """

    @property
    def slug(self) -> str:
        slug = f"{self.owner}/{self.name}"
        return encode_string(slug)
    
    @property
    def version(self) -> str | None:
        if self.latest_version is not None and "id" in self.latest_version:
            return self.latest_version["id"]
        return None

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        data = super().model_dump(*args, **kwargs)
        data["slug"] = self.slug
        data["version"] = self.version
        del data["owner"]

        if "default_example" in data and data["default_example"]:
            data["default_example"] = {
                "input": data["default_example"]["input"],
                "output": data["default_example"]["output"],
            }

        return data


class ProviderModelList(BaseModel):
    models: list[ProviderModel]
