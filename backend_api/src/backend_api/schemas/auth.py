from pydantic import BaseModel
from siwe import SiweMessage


class SiweAuthModel(BaseModel):
    message: SiweMessage


class VerifyModel(BaseModel):
    message: SiweMessage
    address: str


class PayloadModel(BaseModel):
    address: str


class TokenModel(BaseModel):
    access_token: str


class UserModel(BaseModel):
    address: str
