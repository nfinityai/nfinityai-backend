

from datetime import datetime

from sqlmodel import Field, SQLModel


class Usage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.id')
    credits_spent: float = Field(nullable=False)
    request_signature: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
