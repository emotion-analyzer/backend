from dataclasses import dataclass

from scraper.core.schemas import FetchRequest, Post
from scraper.core.scraping import Scraper
import httpx


@dataclass
class BlueskyScraper(Scraper):

    def __init__(self):
        self.bluesky = "https://api.bsky.app"
        self.search_url = self.bluesky + "/xrpc/app.bsky.feed.searchPosts"

    async def query(self, fetch_request: FetchRequest) -> list[Post]:
        """Return relevant posts according to the fetch request."""
        submission_list = []
        params = {'q': fetch_request.query, 'limit': fetch_request.limit, 'lang': 'es'}
        async with httpx.AsyncClient() as client:
            request = await client.get(self.search_url, params=params)
            for post in request.json()["posts"]:
                submission_list.append({"id": post["uri"],
                                        "text": post["record"]["text"],
                                        "timestamp": post["record"]["createdAt"]})
        return submission_list
