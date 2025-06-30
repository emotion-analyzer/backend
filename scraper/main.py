# ruff: noqa: RUF006
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Query
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from scraper.config import config
from scraper.core.bluesky import BlueskyScraper
from scraper.core.queue_middleware import initialize_channel
from scraper.core.reddit import RedditScraper
from scraper.core.schemas import  EmotionalAnalysisParams
from scraper.exceptions.exceptions import ScraperError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scrapers and create the RabbitMQ connection before the app runs."""
    channel = await initialize_channel(config)
    app.state.scrapers = {"reddit": RedditScraper("reddit", channel),
                          "bluesky": BlueskyScraper("bluesky", channel)}
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/posts/")
async def get_social_media_posts (query: Annotated[EmotionalAnalysisParams, Query()],
                                  request: Request):
    """Return relevant social media posts according to query parameters."""
    post_list = []
    try:
        scrapers = []
        if "all" in query.platform:
            scrapers = app.state.scrapers.values()
        else:
            for platform in query.platform:
                scraper = request.app.state.scrapers.get(platform)
                if scraper is None:
                    raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                        detail="Al menos una de las redes sociales especificadas es invalida")
                scrapers.append(scraper)
        for scraper in scrapers:
            posts = await scraper.query(query)
            post_list.extend(posts)
    except ScraperError as e:
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE,
                            detail=e.message) from e
    return {"posts": post_list}
