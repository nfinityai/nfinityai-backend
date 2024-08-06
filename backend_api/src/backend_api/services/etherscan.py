import aiohttp
import aiohttp_retry
from backend_api.backend.config import Settings
from aiocache import cached


class EtherscanService:
    BASE_API_URL = "https://api.etherscan.io/api"

    def __init__(self, settings: Settings):
        self._settings = settings
        self.session = aiohttp.ClientSession()
        retry_options = aiohttp_retry.ExponentialRetry(
            attempts=self._settings.provider_api_retry_attempts,
            factor=self._settings.provider_api_factor,
        )
        self.client = aiohttp_retry.RetryClient(
            client_session=self.session, retry_options=retry_options
        )

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.__aexit__(*args, **kwargs)
        await self.session.close()

    @cached(ttl=60 * 5)
    async def get_contract_abi(self, contract_address: str) -> dict:
        api_key = self._settings.etherscan_api_key
        url = (
            f"{self.BASE_API_URL}?module=contract&action=getabi&address={contract_address}&"
            f"apikey={api_key}"
        )
        async with self.client.get(url, raise_for_status=True) as response:
            data = await response.json()
            if data["status"] == "1":
                return data["result"]
            else:
                raise Exception(f"Error fetching ABI: {data['result']}")
