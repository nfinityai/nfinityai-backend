from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from backend_api.backend.config import get_settings


def get_default_balance_amount() -> int:
    settings = get_settings()
    if settings.free_trial_mode:
        return settings.free_trial_credits
    return 0


class Balance(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    amount: float = Field(default_factory=get_default_balance_amount, nullable=False)


class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class Transaction(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    amount: float = Field(nullable=False)
    transaction_type: TransactionType = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
