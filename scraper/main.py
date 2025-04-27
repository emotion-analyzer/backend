# ruff: noqa: RUF006
import asyncio
from contextlib import asynccontextmanager
import json
import random as random_module

import asyncpraw
from fastapi import FastAPI

from scraper.config import config
from scraper.scraping import initiate_scraping


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the hourly scraper before the app runs."""
    asyncio.create_task(initiate_scraping())
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    """Hello world function."""
    return {"message": "Hello World"}


@app.get("/random")
async def random(limit: int = 10):
    """Return {limit} top submissions from a random subreddit."""
    reddit = asyncpraw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        user_agent=config.USER_AGENT,
        ratelimit_seconds=config.RATELIMIT_SECONDS
    )
    random_subreddit = random_module.choice(config.ES_SUBREDDITS)
    submission_list = []
    subreddit = await reddit.subreddit(random_subreddit)
    async for submission in subreddit.hot(limit=limit):
        submission_list.append(submission.selftext)
    return {"subreddit": random_subreddit,
            "submissions": json.dumps(submission_list)}
