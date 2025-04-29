from dataclasses import dataclass, field

import asyncpraw
from scraper.config import config
from scraper.core.schemas import FetchRequest, Post
from scraper.core.scraping import Scraper


@dataclass
class RedditScraper(Scraper):
    reddit: asyncpraw.Reddit = field(init=False)

    # Class variable to enforce singleton
    _instance: "RedditScraper" = field(default=None, init=False, repr=False)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __post_init__(self):
        # Only runs once
        if not hasattr(self, "reddit"):
            self.reddit = asyncpraw.Reddit(
                client_id=config.REDDIT.CLIENT_ID,
                client_secret=config.REDDIT.CLIENT_SECRET,
                user_agent=config.REDDIT.USER_AGENT,
                ratelimit_seconds=config.REDDIT.RATELIMIT_SECONDS
            )

    async def initiate_scraping(self):
        """Initiate hourly scraping."""
        pass

    async def query(self, fetch_request: FetchRequest) -> list[Post]:
        """Return relevant posts according to the fetch request."""
        submission_list = []
        count = 0
        subreddit = await self.reddit.subreddit(config.REDDIT.ES_SUBREDDITS)
        async for submission in subreddit.new(limit=None):
            if fetch_request.query in submission.selftext:
                submission_list.append({"id": submission.id,
                                        "text": submission.selftext,
                                        "timestamp": submission.created_utc})
                count += 1
                if count == fetch_request.limit:
                    break
        return submission_list

def get_reddit_scraper() -> RedditScraper:
    return RedditScraper()