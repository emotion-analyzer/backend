# ruff: noqa: RUF006
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_502_BAD_GATEWAY, HTTP_503_SERVICE_UNAVAILABLE, \
    HTTP_404_NOT_FOUND

from scraper.core.bluesky import BlueskyScraper
from scraper.core.reddit import RedditScraper
from scraper.core.schemas import FetchRequest, FetchResult
from scraper.exceptions.exceptions import ScraperError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scrapers before the app runs."""
    app.state.scrapers = {"reddit": RedditScraper(), "bluesky": BlueskyScraper()}
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/fetch")
async def fetch_posts(fetch_req: FetchRequest, request: Request) -> FetchResult:
    """Return relevant social media posts according to query parameters."""
    try:
        scraper = request.app.state.scrapers.get(fetch_req.platform)
        if scraper is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="La red social especificada es invalida")
        matching_posts = await scraper.query(fetch_req)
    except ScraperError as e:
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail=e.message) from e
    return {"results": matching_posts}
