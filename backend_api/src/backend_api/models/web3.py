from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, Column


class Web3Event(SQLModel):
    event_id: str = Field(default=None, primary_key=True)
    block_number: int = Field(nullable=False)
    transaction_hash: str = Field(nullable=False)
    log_index: int = Field(nullable=True)
    address: str = Field(nullable=False)
    event_name: str = Field(nullable=False)
    event_hash: str = Field(nullable=False)
    data: dict = Field(default_factory=dict, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    class Config:
        arbitrary_types_allowed = True
