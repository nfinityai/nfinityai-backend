from datetime import datetime, timedelta

from pydantic import BaseModel, Field, computed_field
from siwe import SiweMessage

from backend_api.backend.config import get_settings
from backend_api.models.balance import (
    CurrencyToPayEnum,
    TransactionStatus,
    TransactionType,
)


class SiweBalanceModel(BaseModel):
    message: SiweMessage


class Balance(BaseModel):
    user_id: int
    amount: float


class CreateBalance(BaseModel):
    user_id: int


class BalanceModel(BaseModel):
    amount: float


class CreateTransaction(BaseModel):
    user_id: int
    amount: float
    type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)


class Transaction(CreateTransaction):
    id: int
    finished_at: datetime | None = None


class TransactionList(BaseModel):
    transactions: list[Transaction]


class UpdateTransactionCompleted(Transaction):
    status: TransactionStatus = TransactionStatus.COMPLETED
    finished_at: datetime = Field(default_factory=datetime.now)


class UpdateTransactionFailed(Transaction):
    status: TransactionStatus = TransactionStatus.FAILED
    finished_at: datetime = Field(default_factory=datetime.now)


class BalancePopupModel(BaseModel):
    id: int
    user_id: int
    price_usd: float
    address_to_pay: str
    currency_to_pay: CurrencyToPayEnum
    time_to_pay_minutes: int
    pay_until: datetime

    created_at: datetime
    finished_at: datetime | None


class CreateBalancePopupModel(BaseModel):
    user_id: int
    price_usd: float
    currency_to_pay: CurrencyToPayEnum

    created_at: datetime = Field(..., default_factory=datetime.now)

    @computed_field
    @property
    def time_to_pay_minutes(self) -> int:
        return get_settings().time_to_pay_minutes

    @computed_field
    @property
    def pay_until(self) -> datetime:
        return datetime.now() + timedelta(minutes=self.time_to_pay_minutes)

    @computed_field
    @property
    def address_to_pay(self) -> str:
        return get_settings().contract_address


class UpdateBalancePopupModel(BaseModel):
    id: int
    finished_at: datetime = Field(..., default_factory=datetime.now)


class BalancePopupCurrenciesListModel(BaseModel):
    currencies: list[CurrencyToPayEnum] = CurrencyToPayEnum.get_list()
