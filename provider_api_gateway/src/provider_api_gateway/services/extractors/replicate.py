import requests
from bs4 import BeautifulSoup
from provider_api_gateway.logging import get_logger

logger = get_logger(__name__)


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

    def get_run_time_and_cost(self):
        html_content = self.fetch_page()
        run_time_and_cost_info = self.parse_content(html_content)
        return run_time_and_cost_info
