# ruff: noqa: RUF006
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from scraper.core.bluesky import BlueskyScraper
from scraper.core.reddit import RedditScraper
from scraper.core.schemas import FetchRequest, FetchResult


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scrapers before the app runs."""
    app.state.scrapers = {"reddit": RedditScraper(), "bluesky": BlueskyScraper()}
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/fetch")
async def fetch_posts(fetch_req: FetchRequest, request: Request) -> FetchResult:
    """Return relevant social media posts according to query parameters."""
    scrapers = request.app.state.scrapers
    # Pagination missing
    matching_posts = await scrapers.get(fetch_req.platform).query(fetch_req)
    return {"results": matching_posts}
