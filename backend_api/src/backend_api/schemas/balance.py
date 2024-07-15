from pydantic import BaseModel


class Credit(BaseModel):
    balance: float