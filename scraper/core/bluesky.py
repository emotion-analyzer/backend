from dataclasses import dataclass

from starlette.status import HTTP_200_OK

from scraper.config import config
from scraper.core.schemas import FetchRequest, Post
from scraper.core.scraping import Scraper
import httpx

from scraper.exceptions.exceptions import ScraperError


@dataclass
class BlueskyScraper(Scraper):

    def __init__(self):
        self.bluesky = config.BLUESKY.BASE_URL
        self.search_url = self.bluesky + config.BLUESKY.SEARCH_URL

    async def query(self, fetch_request: FetchRequest) -> list[Post]:
        """Return relevant Bluesky posts according to the fetch request."""
        submission_list = []
        params = {'q': fetch_request.query, 'limit': fetch_request.limit, 'lang': 'es'}
        async with httpx.AsyncClient() as client:
            request = await client.get(self.search_url, params=params)
            if request.status_code != HTTP_200_OK:
                raise ScraperError(request.status_code, "Bluesky")
            for post in request.json()["posts"]:
                submission_list.append({"id": post["uri"],
                                        "text": post["record"]["text"],
                                        "timestamp": post["record"]["createdAt"]})
        return submission_list
