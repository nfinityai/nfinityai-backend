from pydantic import BaseModel


class User(BaseModel):
    id: int
    address: str


class UserModel(BaseModel):
    address: str


class CreateUser(BaseModel):
    address: str
