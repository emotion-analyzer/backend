from dataclasses import dataclass
import re

import aiohttp
import asyncpraw
import asyncprawcore.exceptions
from util.codes import POST
from util.schemas import AnalysisRequest, Post

from scraper.config import config
from scraper.core.metrics import posts_scraped
from scraper.core.scraper import Scraper


@dataclass
class RedditScraper(Scraper):
    """Executes real-time Reddit search queries."""

    def __init__(self, name, channel, languages, logger):
        super().__init__(name, channel, languages, logger)
        self.reddit = asyncpraw.Reddit(
            client_id=config.REDDIT.CLIENT_ID,
            client_secret=config.REDDIT.CLIENT_SECRET,
            user_agent=config.REDDIT.USER_AGENT,
            ratelimit_seconds=config.REDDIT.RATELIMIT_SECONDS
        )
        self.reddit.read_only = True

    def normalize(self, text: str) -> str:
        """Normalize Reddit subreddit and user tokens."""
        text = super().normalize(text)
        text = re.sub(r'/?r/[\w\-]+', '<SUBREDDIT>', text)
        text = re.sub(r'/?u/[\w\-]+', '<USER>', text)
        return text

    async def query(self, query: AnalysisRequest) -> int:
        """Return relevant posts according to the fetch request."""
        messages_sent = 0
        if not self.validate_query(query):
            return messages_sent
        if query.parameters.language == "es":
            subreddit = await self.reddit.subreddit(config.REDDIT.ES_SUBREDDITS)
        elif query.parameters.language == "en":
            subreddit = await self.reddit.subreddit(config.REDDIT.EN_SUBREDDITS)
        keyword = ' '.join(query.parameters.keywords)
        try:
            async for submission in subreddit.search(query=keyword,
                                                 sort="new",
                                                 limit=config.REDDIT.LIMIT):
                if submission.selftext == "":
                    continue
                if submission.created_utc < query.parameters.from_.timestamp():
                    continue
                reddit_post = Post(source="reddit",
                                   link=f"reddit.com{submission.permalink}",
                                   text=self.normalize(submission.selftext),
                                   timestamp=submission.created_utc,
                                   code = POST,
                                   query_processor_id=query.query_processor_id,
                                   model=query.parameters.model,
                                   language=query.parameters.language)
                await self.send_to_analyzer(reddit_post)
                messages_sent += 1
        except asyncprawcore.NotFound:
            self.logger.error(f"Subreddit not found: {subreddit.display_name}")
        except asyncprawcore.Forbidden:
            self.logger.error("Forbidden: missing scopes or banned")
        except asyncprawcore.OAuthException:
            self.logger.error("OAuth authentication failure")
        except asyncprawcore.ServerError:
            self.logger.error("Reddit server error")
        except asyncprawcore.ResponseException as e:
            self.logger.error(f"Bad HTTP status from Reddit: {e}")
        except asyncprawcore.RequestException as e:
            self.logger.error(f"Request failed: {e}")
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {e}")
        except TimeoutError:
            self.logger.error("Timeout while querying Reddit")
        except Exception as e:
            self.logger.exception(f"Unexpected error during reddit.search: {e}")
        posts_scraped.labels(platform="reddit",
                             language=query.parameters.language).inc(messages_sent)
        self.logger.info(f"Scraped {messages_sent} Reddit posts")
        return messages_sent
