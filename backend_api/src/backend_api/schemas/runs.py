from pydantic import BaseModel, computed_field
from siwe import SiweMessage


class SiweRunModel(BaseModel):
    message: SiweMessage

    @computed_field
    @property
    def prepared_message(self) -> str:
        return self.message.prepare_message()
