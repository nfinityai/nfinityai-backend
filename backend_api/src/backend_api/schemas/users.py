from pydantic import BaseModel


class User(BaseModel):
    id: int
    wallet_address: str


class UserModel(BaseModel):
    wallet_address: str


class CreateUser(BaseModel):
    wallet_address: str
