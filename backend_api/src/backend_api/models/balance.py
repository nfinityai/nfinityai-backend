from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field

class Credit(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key='user.id')
    balance: float = Field(default=0, nullable=False)


class TransactionType(str, Enum):
    DEBIT = 'debit'
    CREDIT = 'credit'


class Transaction(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key='user.id')
    amount: float = Field(nullable=False)
    transaction_type: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
