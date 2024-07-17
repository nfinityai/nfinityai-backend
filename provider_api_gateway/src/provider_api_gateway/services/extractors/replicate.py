from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel, Field, computed_field, field_validator
import requests
from bs4 import BeautifulSoup
import re
from provider_api_gateway.config import Settings, get_settings
from provider_api_gateway.logging import get_logger
from provider_api_gateway.schemas.types import ProviderHardwareEnum
import pandas as pd

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

    @field_validator("prediction_time", mode='before')
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
    def __init__(self, url: str):
        self.url = url

    def fetch_page(self):
        response = requests.get(self.url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text

    def parse_content(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the "Run time and cost" section
        section_header = soup.find("h4", string="Run time and cost")

        if not section_header:
            logger.warning("Run time and cost section not found", url=self.url)
            return None

        # Assuming the information is within the next sibling element
        section_content = section_header.find_next_sibling("p")

        if not section_content:
            logger.warning("Run time and cost content not found", url=self.url)
            return None

        return section_content.get_text(strip=True)

    def extract_gpu_and_prediction_time(self, run_time_and_cost) -> CostInfoModel:
        """Extract GPU and prediction time from run_time_and_cost string using regex."""
        gpu_pattern = r"runs on (.+?) hardware"
        prediction_time_pattern = r"complete within (\d+) seconds"

        gpu_match = re.search(gpu_pattern, run_time_and_cost)
        prediction_time_match = re.search(prediction_time_pattern, run_time_and_cost)

        gpu = gpu_match.group(1) if gpu_match else None
        prediction_time = prediction_time_match.group(1) if prediction_time_match else None

        if not gpu or not prediction_time:
            logger.warning("Failed to extract GPU and prediction time", content=run_time_and_cost)

        return CostInfoModel(name=gpu, prediction_time=prediction_time)  # type: ignore

    def get_run_time_and_cost(self):
        html_content = self.fetch_page()
        run_time_and_cost_info = self.parse_content(html_content)
        if run_time_and_cost_info:
            extracted_info = self.extract_gpu_and_prediction_time(run_time_and_cost_info)
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
            return float(second_price.replace('$', '').replace('/sec', ''))
        except ValueError:
            return None

    @computed_field
    @property
    def price_per_hour(self) -> float | None:
        _, hour_price = self.price.rsplit(maxsplit=1)
        try:
            return float(hour_price.replace('$', '').replace('/hr', ''))
        except ValueError:
            return None

    @field_validator("gpu_count", "cpu_count", mode='before')
    @classmethod
    def validate_count(cls, v):
        if not isinstance(v, str):
            raise ValueError("Count must be a string")
        try:
            return int(v.replace('x', ''))
        except ValueError:
            return 0

    @field_validator("gpu_ram_gb", "ram_gb", mode='before')
    @classmethod
    def validate_ram(cls, v):
        if not isinstance(v, str):
            raise ValueError("RAM must be a string")
        try:
            return float(v.replace('GB', ''))
        except ValueError:
            return 0


class ReplicateHardwareCostExtractor:
    def __init__(self, url):
        self.url = url


    def fetch_page(self):
        response = requests.get(self.url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text

    def get_cost_table(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the table by using the heading <h2> as an anchor
        heading = soup.find('h2', text='Pricing')
        if not heading:
            return None
        table = heading.find_next('table')
        if not table:
            return None
        
        table_head = table.find('thead')
        if not table_head:
            return None
        # Extract column names
        columns = [th.get_text(strip=True) for th in table_head.find_all('th')]  # type: ignore


        table_body = table.find('tbody')
        if not table_body:
            return None
        # Extract table rows

        rows = []
        for tr in table_body.find_all('tr'):  # type: ignore
            cells = {}
            for i, td in enumerate(tr.find_all('td')):
                cell_content = " ".join(td.stripped_strings)
                cells[columns[i]] = cell_content
            rows.append(HardwareCostModel(**cells).model_dump())

        return pd.DataFrame(rows)
    
    def extract_cost_info(self) -> pd.DataFrame | None:
        html_content = self.fetch_page()
        cost_table  = self.get_cost_table(html_content)
        
        return cost_table


def get_cost_table_extractor(settings: Annotated[Settings, Depends(get_settings)]):
    return ReplicateHardwareCostExtractor(settings.replicate_hardware_pricing_url)
