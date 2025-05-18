# ruff: noqa: RUF006
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from scraper.core.reddit import RedditScraper
from scraper.core.schemas import FetchRequest, FetchResult
from scraper.core.twitter import TwitterScraper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scrapers before the app runs."""
    app.state.scrapers = {"reddit": RedditScraper(),
                          "twitter": TwitterScraper()}
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/fetch")
def fetch_posts(fetch_req: FetchRequest, request: Request) -> FetchResult:
    """Return relevant social media posts according to query parameters."""
    scrapers = request.app.state.scrapers
    matching_posts = scrapers.get(fetch_req.platform).query(fetch_req)
    return {"results": matching_posts}
