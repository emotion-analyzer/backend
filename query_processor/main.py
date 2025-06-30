# ruff: noqa: RUF006
from typing import Annotated

from fastapi import FastAPI, Query, HTTPException

from query_processor.core.schemas import EmotionalAnalysisParams
from query_processor.config import config

import httpx


timeout = httpx.Timeout(
    connect=config.HTTPX.CONNECTION_TIMEOUT,  # connect timeout
    read=config.HTTPX.CONNECTION_TIMEOUT,  # read timeout
    write=config.HTTPX.CONNECTION_TIMEOUT,  # timeout for sending request
    pool=config.HTTPX.CONNECTION_TIMEOUT  # read timeout
)

app = FastAPI()

@app.get("/")
async def get_emotional_analysis (query: Annotated[EmotionalAnalysisParams, Query()]):
    """Request social media posts and their corresponding emotional analysis."""
    try:
        async with httpx.AsyncClient() as client:
            # This doesn't scale. Need to think of a way to make it so (maybe message broker?)
            # Hash query here before proceeding. Check for that hash as well.
            posts = await client.get(url=config.SCRAPER.URL,
                                     params=query.model_dump(exclude_unset=True))
            posts.raise_for_status()
            request = await client.post(url=config.ANALYZER.URL,
                                        json=posts.json())
            request.raise_for_status()
            return request.json()
    except  httpx.HTTPStatusError as exception:
        raise HTTPException(status_code=exception.response.status_code,
                            detail= exception.response.json()["detail"])

