from datetime import datetime, timedelta

from pydantic import BaseModel, Field, computed_field
from siwe import SiweMessage

from backend_api.backend.config import get_settings
from backend_api.models.balance import TransactionStatus, TransactionType


class SiweBalanceModel(BaseModel):
    message: SiweMessage


class Balance(BaseModel):
    user_id: int
    amount: float


class CreateBalance(BaseModel):
    user_id: int


class BalanceModel(BaseModel):
    amount: float


class BalancePopupModel(BaseModel):

    @computed_field@property
    def time_to_pay_minutes(self) -> int:
        return get_settings().time_to_pay_minutes
    
    @computed_field
    @property
    def address(self) -> str:
        return get_settings().contract_address


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
