from pydantic import BaseModel


class User(BaseModel):
    address: str


class UserModel(BaseModel):
    address: str


class CreateUser(BaseModel):
    address: str
