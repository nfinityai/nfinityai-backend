from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, computed_field, field_validator

from provider_api_gateway.schemas.types import ProviderRunStateEnum


class RunResultModel(BaseModel):
    error: str | None = None
    output: Any | None = None
    metrics: dict | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def elapsed_time(self) -> float | None:
        if self.metrics and "predict_time" in self.metrics:
            return float(self.metrics["predict_time"])
        return None


class Run(BaseModel):
    id: str
    status: ProviderRunStateEnum
    created_at: datetime | None = None

    @field_validator("status", mode="before")
    def validate_status(cls, v):
        state = str(v)
        if state in ["pending", "starting"]:
            return ProviderRunStateEnum.PENDING
        if state in ["running", "started", "processing"]:
            return ProviderRunStateEnum.RUNNING
        if state in ["completed", "finished", "succeeded"]:
            return ProviderRunStateEnum.COMPLETED
        if state in ["failed", "canceled"]:
            return ProviderRunStateEnum.FAILED
        raise ValueError(f"{state} is not a valid model run status")


class RunResult(Run):
    result: RunResultModel | None = None
    finished_at: datetime | None = Field(default=None, validation_alias="completed_at")
    metrics: dict | None = Field(default=None, exclude=True)


class RunStatus(Run):
    pass
