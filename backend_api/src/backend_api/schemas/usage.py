

from datetime import datetime

from pydantic import BaseModel, Field


class Usage(BaseModel):
    user_id: int
    credits_spent: float
    request_signature: str
    created_at: datetime = Field(default_factory=datetime.now)


class CreateUsage(BaseModel):
    user_id: int
    model_id: int
    transaction_id: int | None = None
    credits_spent: float
    request_signature: str
    created_at: datetime = Field(default_factory=datetime.now)
    finished_at: datetime | None = None
