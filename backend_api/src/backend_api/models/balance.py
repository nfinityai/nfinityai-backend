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


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Transaction(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    amount: float = Field(nullable=False)
    type: TransactionType = Field(nullable=False)
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    finished_at: datetime = Field(default=None, nullable=True)


class CurrencyToPayEnum(str, Enum):
    ETH = "ETH"
    USDT = "USDT"

    @classmethod
    def get_list(cls):
        return [currency for currency in cls]


class BalancePopup(SQLModel, table=True):
    __tablename__ = "balance_popups"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    price_usd: float = Field(nullable=False)
    address_to_pay: str = Field(nullable=False)
    currency_to_pay: CurrencyToPayEnum = Field(nullable=False)
    time_to_pay_minutes: int = Field(nullable=False)
    pay_until: datetime = Field(nullable=False)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    finished_at: datetime = Field(default=None, nullable=True)
