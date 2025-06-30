from dataclasses import dataclass

import httpx
from scraper.config import config
from scraper.core.schemas import Post, EmotionalAnalysisParams
from scraper.core.scraping import Scraper
from scraper.exceptions.exceptions import ScraperError
from starlette.status import HTTP_200_OK


@dataclass
class BlueskyScraper(Scraper):
    """Executes real-time Bluesky search queries."""

    def __init__(self, name, channel):
        super().__init__(name, channel)
        self.bluesky = config.BLUESKY.BASE_URL
        self.search_url = self.bluesky + config.BLUESKY.SEARCH_URL

    async def query(self, query: EmotionalAnalysisParams):
        """Return relevant Bluesky posts according to the fetch request."""
        submission_list = []
        params = {'q': query.keyword, 'limit': query.limit, 'lang': 'es',
                  'since': query.date_start.isoformat(), 'until': query.date_end.isoformat()}
        async with httpx.AsyncClient() as client:
            request = await client.get(self.search_url, params=params)
            if request.status_code != HTTP_200_OK:
                raise ScraperError(request.status_code, "Bluesky")
            for post in request.json()["posts"]:
                bsky_post = Post(link=f"https://bsky.app/profile/{post['author']['handle']}/post/{post['uri'].split('/')[-1]}",
                                 text=post["record"]["text"],
                                 timestamp=post["record"]["createdAt"])
                await self.send_to_analyzer(bsky_post)
                submission_list.append(bsky_post)
        return submission_list
