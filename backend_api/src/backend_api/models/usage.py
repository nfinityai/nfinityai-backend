

from datetime import datetime
from sqlmodel import SQLModel, Field


class Usage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='user.id')
    model_id: str = Field(nullable=False)
    credits_spent: float = Field(nullable=False)
    request_signature: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
