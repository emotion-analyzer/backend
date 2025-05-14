# ruff: noqa: RUF006
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from scraper.core.reddit import get_reddit_scraper
from scraper.core.schemas import FetchRequest, FetchResult
from scraper.core.twitter import TwitterScraper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scrapers before the app runs."""
    app.state.scrapers = {"REDDIT": get_reddit_scraper()}
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/fetch")
async def fetch_posts(fetch_req: FetchRequest, request: Request) -> FetchResult:
    """Return relevant social media posts according to query parameters."""
    scrapers = request.app.state.scrapers
    match fetch_req.platform:
        case "reddit":
            scraper = scrapers["REDDIT"]
        case "twitter":
            scraper = await TwitterScraper.login_create()
        case _:
            return {"results": []}
    matching_posts = await scraper.query(fetch_req)
    return {"results": matching_posts}
