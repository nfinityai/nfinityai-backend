from typing import Annotated
import aiohttp
import aiohttp_retry
from fastapi import Depends
from backend_api.backend.config import Settings, get_settings


from enum import Enum


class TokenToCoinIDEnum(str, Enum):
    ETH = "ethereum"
    USDT = "tether"

    def __str__(self) -> str:
        return self.value


class CoingeckoService:
    BASE_API_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, settings: Settings):
        self._settings = settings
        session = aiohttp.ClientSession()
        retry_options = aiohttp_retry.ExponentialRetry(
            attempts=self._settings.provider_api_retry_attempts,
            factor=self._settings.provider_api_factor,
        )
        self.client = aiohttp_retry.RetryClient(
            client_session=session, retry=retry_options
        )

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.__aexit__(*args, **kwargs)

    async def get_price(self, coin_id: TokenToCoinIDEnum, vs_currency="usd") -> float:
        url = f"{self.BASE_API_URL}/simple/price?ids={coin_id}&vs_currencies={vs_currency}"

        async with self.client.get(url, raise_for_status=True) as response:
            data = await response.json()
        return data[coin_id][vs_currency]


async def get_coingecko_service(settings: Annotated[Settings, Depends(get_settings)]):
    async with CoingeckoService(settings) as coingecko:
        yield coingecko
