# ruff: noqa:  D102, D103, D105
from dataclasses import dataclass

import asyncpraw
from scraper.config import config
from scraper.core.schemas import FetchRequest, Post
from scraper.core.scraping import Scraper


@dataclass
class RedditScraper(Scraper):
    """Executes real-time Reddit search queries."""

    def __init__(self):
        self.reddit = asyncpraw.Reddit(
            client_id=config.REDDIT.CLIENT_ID,
            client_secret=config.REDDIT.CLIENT_SECRET,
            user_agent=config.REDDIT.USER_AGENT,
            ratelimit_seconds=config.REDDIT.RATELIMIT_SECONDS
        )
        self.reddit.read_only = True


    async def query(self, fetch_request: FetchRequest) -> list[Post]:
        """Return relevant posts according to the fetch request."""
        submission_list = []
        subreddit = await self.reddit.subreddit(config.REDDIT.ES_SUBREDDITS)
        async for submission in subreddit.search(query=fetch_request.query,
                                           sort="new",
                                           limit=None):
            if submission.selftext == "":
                continue
            submission_list.append({"id": submission.id,
                                    "text": submission.selftext,
                                    "timestamp": submission.created_utc})
            if len(submission_list) == fetch_request.limit:
                break
        return submission_list
