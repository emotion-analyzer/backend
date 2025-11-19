from dataclasses import dataclass

import httpx
from starlette.status import HTTP_200_OK
from util.codes import POST
from util.schemas import AnalysisRequest, Post

from scraper.config import config
from scraper.core.scraper import Scraper


@dataclass
class BlueskyScraper(Scraper):
    """Executes real-time Bluesky search queries."""

    def __init__(self, name, channel, languages, logger):
        super().__init__(name, channel, languages, logger)
        self.bluesky = config.BLUESKY.BASE_URL
        self.search_url = self.bluesky + config.BLUESKY.SEARCH_URL

    async def query(self, query: AnalysisRequest) -> int:
        """Return relevant Bluesky posts according to the fetch request."""
        if not self.validate_query(query):
            return 0
        query_string = " OR ".join(query.parameters.keywords)
        params = {'q': query_string,
                  'since': query.parameters.from_.isoformat(),
                  'until': query.parameters.to.isoformat(),
                  'lang': query.parameters.language}
        async with httpx.AsyncClient() as client:
            request = await client.get(self.search_url, params=params)
            if request.status_code != HTTP_200_OK:
                self.logger.warning(f"Error querying Bluesky: {request.text} "
                                    f"({request.status_code})")
                return 0
            messages_sent = len(request.json()["posts"])
            for post in request.json()["posts"]:
                bsky_post = Post(source="bluesky",
                                 link=f"https://bsky.app/profile/{post['author']['handle']}/post/{post['uri'].split('/')[-1]}",
                                 text=post["record"]["text"],
                                 timestamp=post["record"]["createdAt"],
                                 code=POST,
                                 query_processor_id=query.query_processor_id,
                                 model=query.parameters.model,
                                 language=query.parameters.language)
                await self.send_to_analyzer(bsky_post)
        return messages_sent
