# ruff: noqa:  D101, D102, D103, D105, E501
from dataclasses import dataclass

from scraper.core.schemas import FetchRequest, Post
from scraper.core.scraping import Scraper
from twscrape import API


@dataclass
class TwitterScraper(Scraper):
    def __init__(self, api: API):
        self.api = api

    @classmethod
    async def login_create(cls):
        api = API()
        await api.pool.add_account("user1", "pass1",
                                   "u1@example.com", "mail_pass1")
        await api.pool.login_all()
        return cls(api)

    async def initiate_scraping(self):
        """Initiate hourly scraping."""
        pass

    async def query(self, fetch_request: FetchRequest) -> list[Post]:
        submission_list = []
        async for tweet in self.api.search(fetch_request.query, limit=fetch_request.limit):
            submission_list.append({"id": tweet.id,
                                    "text": tweet.text,
                                    "timestamp": tweet.created_utc})
        return submission_list
