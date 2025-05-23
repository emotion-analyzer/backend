# ruff: noqa: T201
from abc import abstractmethod
from dataclasses import dataclass

from scraper.core.schemas import FetchRequest, Post


@dataclass
class Scraper:
    """Scraper base class."""

    @abstractmethod
    def query(self, fetch_request: FetchRequest) -> list[Post]:
        """Search for posts according to the fetch request details."""
