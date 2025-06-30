from dataclasses import dataclass

import asyncpraw
from scraper.config import config
from scraper.core.schemas import FetchQuery, Post
from scraper.core.scraping import Scraper


@dataclass
class RedditScraper(Scraper):
    """Executes real-time Reddit search queries."""

    def __init__(self, name, channel):
        super().__init__(name, channel)
        self.reddit = asyncpraw.Reddit(
            client_id=config.REDDIT.CLIENT_ID,
            client_secret=config.REDDIT.CLIENT_SECRET,
            user_agent=config.REDDIT.USER_AGENT,
            ratelimit_seconds=config.REDDIT.RATELIMIT_SECONDS
        )
        self.reddit.read_only = True


    async def query(self, query: FetchQuery)  -> list[Post]:
        """Return relevant posts according to the fetch request."""
        submission_list = []
        subreddit = await self.reddit.subreddit(config.REDDIT.ES_SUBREDDITS)
        async for submission in subreddit.search(query=query.keyword,
                                                 sort="new",
                                                 limit=None):
            if submission.selftext == "":
                continue
            if submission.created_utc < query.date_start.timestamp():
                break
            reddit_post = Post(link=f"reddit.com{submission.permalink}",
                               text=submission.selftext,
                               timestamp=submission.created_utc)
            await self.send_to_analyzer(reddit_post)
            submission_list.append(reddit_post)
            if len(submission_list) == query.limit:
                break
        return submission_list
