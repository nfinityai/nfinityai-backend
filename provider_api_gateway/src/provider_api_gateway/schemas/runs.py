from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from provider_api_gateway.schemas.types import ProviderRunStateEnum


class RunResultModel(BaseModel):
    error: str | None = None
    output: Any | None = None


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
    finished_at: datetime | None = Field(None, validation_alias="completed_at")


class RunStatus(Run):
    pass
