import json
import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))

class Reddit:
    """Reddit scraping configuration."""
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    USER_AGENT = os.getenv("USER_AGENT")
    ES_SUBREDDITS = "+".join(json.loads(os.getenv("ES_SUBREDDITS")))
    RATELIMIT_SECONDS = int(os.getenv("RATELIMIT_SECONDS"))
    SCRAPER = os.getenv("REDDIT_SCRAPER") == "ON"

class Bluesky:
    """Bluesky scraping configuration."""
    BASE_URL = os.getenv("BASE_URL")
    SEARCH_URL = os.getenv("SEARCH_URL")

class Scraping:
    """MASSive scraper configuration."""
    INITIAL_EMOTIONS = json.loads(os.getenv("INITIAL_EMOTIONS"))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    REDDIT = Reddit
    BLUESKY = Bluesky
    SCRAPING = Scraping


config = Config()
