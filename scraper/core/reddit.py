# ruff: noqa:  D101, D102, D103, D105
from dataclasses import dataclass

import praw

from scraper.config import config
from scraper.core.schemas import FetchRequest, Post
from scraper.core.scraping import Scraper


@dataclass
class RedditScraper(Scraper):

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config.REDDIT.CLIENT_ID,
            client_secret=config.REDDIT.CLIENT_SECRET,
            user_agent=config.REDDIT.USER_AGENT,
            ratelimit_seconds=config.REDDIT.RATELIMIT_SECONDS
        )
        self.reddit.read_only = True

    async def initiate_scraping(self):
        pass

    def query(self, fetch_request: FetchRequest) -> list[Post]:
        """Return relevant posts according to the fetch request."""
        submission_list = []
        subreddit = self.reddit.subreddit(config.REDDIT.ES_SUBREDDITS)
        for submission in subreddit.new(limit=None):
            if fetch_request.query in submission.selftext:
                submission_list.append({"id": submission.id,
                                        "text": submission.selftext,
                                        "timestamp": submission.created_utc})
                if len(submission_list) == fetch_request.limit:
                    break
        return submission_list
