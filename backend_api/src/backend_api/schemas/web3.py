from datetime import datetime
from pydantic import BaseModel, Field, computed_field
from web3 import AsyncWeb3
from backend_api.backend.config import get_settings
from backend_api.exceptions.web3 import Web3EventNotFoundInABIException


class Web3Event(BaseModel):
    event_id: str
    block_hash: str
    block_number: int
    transaction_hash: str
    transaction_index: int
    log_index: int
    address: str
    event_name: str
    event_hash: str
    data: dict


class CreateWeb3Event(BaseModel):
    block_hash: str = Field(..., validation_alias="blockHash")
    block_number: int = Field(..., validation_alias="blockNumber")
    transaction_hash: str = Field(..., validation_alias="transactionHash")
    transaction_index: int = Field(..., validation_alias="transactionIndex")
    log_index: int = Field(..., validation_alias="logIndex")
    address: str
    event_name: int = Field(..., validation_alias="event")
    data: dict = Field(..., validation_alias="args")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @computed_field(return_type=str)
    @property
    def event_id(self) -> str:
        return f"{self.transaction_hash}:{self.log_index}"

    @computed_field(return_type=str)
    @property
    def event_hash(self) -> str:
        abi = get_settings().contract_abi
        event_abi = next(
            (
                item
                for item in abi
                if item["type"] == "event" and item["name"] == self.event_name
            ),
            None,
        )
        if event_abi is None:
            raise Web3EventNotFoundInABIException("Event not found in ABI")
        event_signature = f"{self.event_name}({','.join([input['type'] for input in event_abi['inputs']])})"

        return AsyncWeb3.keccak(text=event_signature).hex()
