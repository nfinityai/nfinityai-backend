from pydantic import BaseModel
from siwe import SiweMessage


class SiweRunModel(BaseModel):
    message: SiweMessage
