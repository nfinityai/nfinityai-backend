from datetime import datetime
from pydantic import BaseModel, Field

from backend_api.models.balance import TransactionType


class Balance(BaseModel):
    user_id: int
    amount: float

class Transaction(BaseModel):
    user_id: int
    amount: float
    transaction_type: TransactionType
    created_at: datetime = Field(default_factory=datetime.now)
