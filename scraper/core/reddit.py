from dataclasses import dataclass

import asyncpraw
from scraper.config import config
from scraper.core.schemas import FetchRequest
from scraper.core.scraping import Scraper

from scraper.core.schemas import Post


@dataclass
class RedditScraper(Scraper):
    """Reddit scraper using AsyncPRAW."""

    reddit = asyncpraw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        user_agent=config.USER_AGENT,
        ratelimit_seconds=config.RATELIMIT_SECONDS
    )

    async def initiate_scraping(self):
        """Initiate hourly scraping."""
        pass

    async def query(self, fetch_request: FetchRequest) -> list[Post]:
        """Return relevant posts according to the fetch request."""
        submission_list = []
        count = 0
        subreddit = await self.reddit.subreddit(config.ES_SUBREDDITS)
        async for submission in subreddit.new(limit=None):
            if fetch_request.query in submission.selftext:
                submission_list.append({"id": submission.id,
                                        "text": submission.selftext,
                                        "timestamp": submission.created_utc})
                count += 1
                if count == fetch_request.limit:
                    break
        return submission_list
