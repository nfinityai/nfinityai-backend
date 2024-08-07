from pydantic import BaseModel, computed_field
from siwe import SiweMessage


class SiweAuthModel(BaseModel):
    message: SiweMessage


    @computed_field
    @property
    def prepared_message(self) -> str:
        return self.message.prepare_message()


class VerifyModel(BaseModel):
    message: SiweMessage
    address: str
    signature: str


class PayloadModel(BaseModel):
    wallet_address: str


class TokenModel(BaseModel):
    access_token: str


class UserModel(BaseModel):
    address: str
