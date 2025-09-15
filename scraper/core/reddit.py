from dataclasses import dataclass

import asyncpraw
from util.codes import POST
from util.schemas import AnalysisRequest, Post

from scraper.config import config
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


    async def query(self, query: AnalysisRequest) -> int:
        """Return relevant posts according to the fetch request."""
        messages_sent = 0
        subreddit = await self.reddit.subreddit(config.REDDIT.ES_SUBREDDITS)
        async for submission in subreddit.search(query=query.parameters.keyword,
                                                 sort="new",
                                                 limit=config.REDDIT.LIMIT):
            if submission.selftext == "":
                continue
            if submission.created_utc < query.parameters.date_start.timestamp():
                break
            reddit_post = Post(source="reddit",
                               link=f"reddit.com{submission.permalink}",
                               text=submission.selftext,
                               timestamp=submission.created_utc,
                               code = POST,
                               query_processor_id=query.query_processor_id,
                               model=query.parameters.model)
            await self.send_to_analyzer(reddit_post)
            messages_sent += 1
        return messages_sent
