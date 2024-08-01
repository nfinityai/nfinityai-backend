from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from eth_typing import ChecksumAddress
from fastapi import Depends
from hexbytes import HexBytes
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import col, select
from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContractEvent
from web3.datastructures import AttributeDict
from web3.types import BlockData

from backend_api.backend.config import Settings, get_settings
from backend_api.backend.logging import get_logger
from backend_api.backend.session import AsyncSession, get_session
from backend_api.exceptions.web3 import (
    Web3UnableToDetermineBlock,
)
from backend_api.models.web3 import Web3Event
from backend_api.schemas.web3 import (
    CreateWeb3Event as CreateWeb3EventSchema,
)
from backend_api.schemas.web3 import (
    Web3Event as Web3EventSchema,
)
from backend_api.services.base import BaseDataManager, BaseService
from backend_api.services.etherscan import EtherscanService

logger = get_logger(__name__)


class Web3Service(BaseService[Web3Event]):
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
    ) -> None:
        super().__init__(session)
        self.settings = settings

    def _get_w3_client(self):
        return AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.settings.infura_base_url))

    async def __aenter__(self):
        self.w3 = self._get_w3_client()
        await self.w3.is_connected()

        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    @staticmethod
    def _normalize_contract_address(address: str) -> ChecksumAddress:
        return AsyncWeb3.to_checksum_address(address)

    async def _get_contract(self):
        return self.w3.eth.contract(
            address=self._normalize_contract_address(self.settings.contract_address),
            abi=self.settings.contract_abi,
        )

    @staticmethod
    def attribute_dict_to_dict(attr_dict) -> dict:
        def _validate_value(item: Any) -> Any:
            if isinstance(item, HexBytes):
                return item.hex()
            return item

        if isinstance(attr_dict, AttributeDict):
            return {
                k: _validate_value(Web3Service.attribute_dict_to_dict(v))
                for k, v in attr_dict.items()
            }
        elif isinstance(attr_dict, list):
            return [Web3Service.attribute_dict_to_dict(item) for item in attr_dict]  # type: ignore
        else:
            return attr_dict

    async def _get_block(self, block_number) -> BlockData:
        return await self.w3.eth.get_block(block_number)

    async def add_events(self):
        """
        Adds events from a specified block or the latest block to the database.

        Retrieves the contract using the contract address from settings, then determines the block to start
        fetching events from. If no block is specified, it starts from the latest block or the block number retrieved
        from the last recorded event in the database. For each event in the contract, the method creates a filter
        and collects all event entries from the specified block. These events are added to the database.

        Raises:
            Web3UnableToDetermineBlock: If the block number cannot be determined.
        """
        contract = await self._get_contract()

        manager = Web3EventManager(self.session)
        from_block = await manager.get_last_block_number()

        block = await self._get_block(from_block or "latest")
        block_number = block.get("number")
        if block_number is None:
            raise Web3UnableToDetermineBlock("Could not get block number")

        await logger.info(f"Adding events from block {block_number}", block_number=block_number)

        for event in contract.events._events:
            event_name = event.get("name")
            if event_name is None:
                continue
            contract_event: AsyncContractEvent = getattr(contract.events, event_name)
            event_filter = contract_event.create_filter(fromBlock=block_number - 3)

            events = await event_filter.get_all_entries()

            try:
                await manager.add_events(
                    [
                        CreateWeb3EventSchema(**event)
                        for event in self.attribute_dict_to_dict(events)
                    ]
                )
            except SQLAlchemyError as e:
                await logger.error("Error adding event", error=e)

            await logger.info(
                f"Added {len(events)} events for {event_name}",
                len_events=len(events),
                event_name=event_name,
            )

    async def get_balance(self, address: str) -> int:
        """
        Get the balance of the specified address in NFNT.

        Args:
            address (str): The address to query the balance for.

        Returns:
            int: The balance of the address in NFNT.
        """

        nfnt_address: str = self.settings.nfnt_contract_address
        balance_nfnt_tokens: int = 0
        try:
            checksum_address = self._normalize_contract_address(nfnt_address)
            async with EtherscanService(settings=self.settings) as etherscan_service:
                abi: dict = await etherscan_service.get_contract_abi(contract_address=nfnt_address)

                nfnt_contract = self.w3.eth.contract(address=checksum_address, abi=abi)
                balance_nfnt = await nfnt_contract.functions.balanceOf(address).call()

                balance_nfnt_tokens = int(balance_nfnt / 1e18)
        except Exception as error:
            await logger.error(f"Getting NFNT balance for {address=}, {error=}")
        return balance_nfnt_tokens

    async def has_sufficient_balance(self, address: str, amount: int) -> bool:
        balance = await self.get_balance(address)
        return balance > amount


class EventTypeEnum(str, Enum):
    DEPOSIT = "Deposit"

    def __str__(self) -> str:
        return self.value


class Web3EventService(BaseService[Web3Event]):
    async def get_deposit_events_since(self, since: datetime) -> list[Web3EventSchema]:
        return await Web3EventManager(self.session).get_deposit_events_since(since)


class Web3EventManager(BaseDataManager[Web3Event]):
    async def get_last_block_number(self) -> int | None:
        stmt = select(Web3Event.block_number).order_by(col(Web3Event.created_at).desc())
        return await self.session.scalar(stmt)

    async def get_event(self, event_id: str) -> Web3EventSchema | None:
        stmt = select(Web3Event).where(Web3Event.event_id == event_id)

        model = await self.get_one(stmt)
        return Web3EventSchema(**model.model_dump()) if model is not None else None

    async def get_deposit_events_since(self, since: datetime) -> list[Web3EventSchema]:
        stmt = select(Web3Event).where(
            Web3Event.event_name == str(EventTypeEnum.DEPOSIT), Web3Event.created_at >= since
        )

        models = await self.get_all(stmt)
        return [Web3EventSchema(**model.model_dump()) for model in models]

    async def add_events(self, events: list[CreateWeb3EventSchema]) -> None:
        await self.add_all([Web3Event(**event.model_dump()) for event in events])

    async def add_event(self, event: CreateWeb3EventSchema) -> Web3EventSchema:
        model = await self.add_one(Web3Event(**event.model_dump()))

        return Web3EventSchema(**model.model_dump())


async def get_web3_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    async with Web3Service(session, settings) as web3_service:
        yield web3_service


async def get_web3_event_service(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return Web3EventService(session)
