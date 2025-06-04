# ruff: noqa: RUF006
import asyncio
import json
from contextlib import asynccontextmanager

from aio_pika import Message, DeliveryMode
from fastapi import FastAPI, HTTPException, Request
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from scraper.config import config
from scraper.core.bluesky import BlueskyScraper
from scraper.core.reddit import RedditScraper
from scraper.core.schemas import FetchRequest, FetchResult
from scraper.exceptions.exceptions import ScraperError
from util.queue_middleware import initialize_channel, send_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize scrapers and create the RabbitMQ connection before the app runs."""
    app.state.scrapers = {"reddit": RedditScraper(),
                          "bluesky": BlueskyScraper()}
    app.state.channel = await initialize_channel(config)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/fetch")
async def fetch_posts(fetch_req: FetchRequest, request: Request) -> FetchResult:
    """Return relevant social media posts according to query parameters."""
    try:
        scraper = request.app.state.scrapers.get(fetch_req.platform)
        if scraper is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                                detail="La red social especificada es invalida")
        matching_posts = await scraper.query(fetch_req)
        message = Message(json.dumps(matching_posts).encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT)
        await send_message(message, app.state.channel, config)
    except ScraperError as e:
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE,
                            detail=e.message) from e
    return {"results": matching_posts}
