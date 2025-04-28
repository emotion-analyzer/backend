# ruff: noqa: RUF006
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from scraper.config import config
from scraper.core.reddit import RedditScraper
from scraper.core.schemas import FetchRequest, FetchResult

from scraper.core.reddit import get_reddit_scraper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the hourly scrapers before the app runs."""
    #Initialize databases for scraping here
    if config.REDDIT_SCRAPER:
        asyncio.create_task(RedditScraper.initiate_scraping())
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/fetch")
async def fetch_posts(fetch_request: FetchRequest) -> FetchResult:
    """Return relevant social media posts according to query parameters."""
    match fetch_request.platform:
        case "reddit":
            scraper = get_reddit_scraper()
        case _:
            return {"results": []}
    matching_posts = await scraper.query(fetch_request)
    return {"results": matching_posts}
