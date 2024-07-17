import re
from http import HTTPStatus
from typing import Annotated

import aiohttp
import aiohttp_retry
import pandas as pd
from bs4 import BeautifulSoup
from fastapi import Depends
from provider_api_gateway.config import Settings, get_settings
from provider_api_gateway.logging import get_logger
from provider_api_gateway.schemas.types import ProviderHardwareEnum
from pydantic import BaseModel, Field, computed_field, field_validator

logger = get_logger(__name__)


class CostInfoModel(BaseModel):
    name: str | None = Field(default=None)
    prediction_time: float | None

    @computed_field
    @property
    def sku(self) -> str | None:
        if not self.name:
            return
        return ProviderHardwareEnum.from_text(self.name)

    @field_validator("prediction_time", mode="before")
    @classmethod
    def validate_time(cls, v):
        if not v:
            return

        try:
            return float(v)
        except ValueError as e:
            logger.error("Failed to convert prediction time to float", exc_info=e, v=v)
        return


class ReplicateModelCostExtractor:
    def __init__(self, client: aiohttp_retry.RetryClient):
        self.client = client

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.__aexit__(*args, **kwargs)

    async def fetch_page(self, url: str):
        async with self.client.get(url) as resp:
            if resp.status != HTTPStatus.OK:
                logger.error("Failed to fetch page", url=url, status=resp.status)
                resp.raise_for_status()
            return await resp.text()

    def parse_content(self, url: str, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the "Run time and cost" section
        section_header = soup.find("h4", string="Run time and cost")

        if not section_header:
            logger.warning("Run time and cost section not found", url=url)
            return None

        # Assuming the information is within the next sibling element
        section_content = section_header.find_next_sibling("p")

        if not section_content:
            logger.warning("Run time and cost content not found", url=url)
            return None

        return section_content.get_text(strip=True)

    def extract_gpu_and_prediction_time(self, run_time_and_cost) -> CostInfoModel:
        """Extract GPU and prediction time from run_time_and_cost string using regex."""
        gpu_pattern = r"runs on (.+?) hardware"
        prediction_time_pattern = r"complete within (\d+) seconds"

        gpu_match = re.search(gpu_pattern, run_time_and_cost)
        prediction_time_match = re.search(prediction_time_pattern, run_time_and_cost)

        gpu = gpu_match.group(1) if gpu_match else None
        prediction_time = (
            prediction_time_match.group(1) if prediction_time_match else None
        )

        if not gpu or not prediction_time:
            logger.warning(
                "Failed to extract GPU and prediction time", content=run_time_and_cost
            )

        return CostInfoModel(name=gpu, prediction_time=prediction_time)  # type: ignore

    async def get_run_time_and_cost(self, url):
        html_content = await self.fetch_page(url)
        run_time_and_cost_info = self.parse_content(url, html_content)
        if run_time_and_cost_info:
            extracted_info = self.extract_gpu_and_prediction_time(
                run_time_and_cost_info
            )
            return extracted_info
        return None


class HardwareCostModel(BaseModel):
    hardware: str = Field(..., alias="Hardware", exclude=True)
    price: str = Field(..., alias="Price", exclude=True)
    gpu_count: int = Field(..., validation_alias="GPU")
    cpu_count: int = Field(..., validation_alias="CPU")
    gpu_ram_gb: int = Field(..., validation_alias="GPU RAM")
    ram_gb: int = Field(..., validation_alias="RAM")

    @computed_field
    @property
    def name(self) -> str:
        name, sku = self.hardware.rsplit(maxsplit=1)
        return name

    @computed_field
    @property
    def sku(self) -> str:
        return self.hardware.split(" ")[-1]

    @computed_field
    @property
    def price_per_second(self) -> float | None:
        second_price, _ = self.price.rsplit(maxsplit=1)
        try:
            return float(second_price.replace("$", "").replace("/sec", ""))
        except ValueError:
            return None

    @computed_field
    @property
    def price_per_hour(self) -> float | None:
        _, hour_price = self.price.rsplit(maxsplit=1)
        try:
            return float(hour_price.replace("$", "").replace("/hr", ""))
        except ValueError:
            return None

    @field_validator("gpu_count", "cpu_count", mode="before")
    @classmethod
    def validate_count(cls, v):
        if not isinstance(v, str):
            raise ValueError("Count must be a string")
        try:
            return int(v.replace("x", ""))
        except ValueError:
            return 0

    @field_validator("gpu_ram_gb", "ram_gb", mode="before")
    @classmethod
    def validate_ram(cls, v):
        if not isinstance(v, str):
            raise ValueError("RAM must be a string")
        try:
            return float(v.replace("GB", ""))
        except ValueError:
            return 0


class ReplicateHardwareCostExtractor:
    def __init__(self, client: aiohttp_retry.RetryClient):
        self.client = client

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.__aexit__(*args, **kwargs)

    async def fetch_page(self, url: str):
        async with self.client.get(url) as resp:
            if resp.status != HTTPStatus.OK:
                logger.error("Failed to fetch page", url=url, status=resp.status)
                resp.raise_for_status()
            return await resp.text()

    def get_cost_table(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the table by using the heading <h2> as an anchor
        heading = soup.find("h2", text="Pricing")
        if not heading:
            return None
        table = heading.find_next("table")
        if not table:
            return None

        table_head = table.find("thead")
        if not table_head:
            return None
        # Extract column names
        columns = [th.get_text(strip=True) for th in table_head.find_all("th")]  # type: ignore

        table_body = table.find("tbody")
        if not table_body:
            return None
        # Extract table rows

        rows = []
        for tr in table_body.find_all("tr"):  # type: ignore
            cells = {}
            for i, td in enumerate(tr.find_all("td")):
                cell_content = " ".join(td.stripped_strings)
                cells[columns[i]] = cell_content
            rows.append(HardwareCostModel(**cells).model_dump())

        return pd.DataFrame(rows)

    async def extract_cost_info(self, url: str) -> pd.DataFrame | None:
        html_content = await self.fetch_page(url)
        cost_table = self.get_cost_table(html_content)

        return cost_table


def get_retry_options(
    settings: Annotated[Settings, Depends(get_settings)],
) -> aiohttp_retry.ExponentialRetry:
    return aiohttp_retry.ExponentialRetry(
        attempts=settings.extractor_retry_attempts,
        factor=settings.extractor_retry_factor,
    )


async def get_session() -> aiohttp.ClientSession:
    return aiohttp.ClientSession()


async def get_retry_client(
    session: Annotated[aiohttp.ClientSession, Depends(get_session)],
    retry_options: Annotated[
        aiohttp_retry.RetryOptionsBase, Depends(get_retry_options)
    ],
) -> aiohttp_retry.RetryClient:
    return aiohttp_retry.RetryClient(client_session=session, retry=retry_options)


async def get_replicate_model_cost_extractor(
    client: Annotated[aiohttp_retry.RetryClient, Depends(get_retry_client)],
):
    async with ReplicateModelCostExtractor(client) as extractor:
        yield extractor


async def get_cost_table_extractor(
    client: Annotated[aiohttp_retry.RetryClient, Depends(get_retry_client)],
):
    async with ReplicateHardwareCostExtractor(client) as extractor:
        yield extractor
