import json
import os

from dotenv import load_dotenv

# This could be fancier/more structured
if os.getenv("TESTING"):
    load_dotenv(".env.test")
else:
    # This should load the production env
    load_dotenv(".env.test")

class Reddit:
    """Reddit scraping configuration."""
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    USER_AGENT = os.getenv("USER_AGENT")
    ES_SUBREDDITS = "+".join(json.loads(os.getenv("ES_SUBREDDITS")))
    RATELIMIT_SECONDS = int(os.getenv("RATELIMIT_SECONDS"))
    SCRAPER = os.getenv("REDDIT_SCRAPER") == "ON"

class Scraping:
    """MASSive scraper configuration."""
    INITIAL_EMOTIONS = json.loads(os.getenv("INITIAL_EMOTIONS"))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    REDDIT = Reddit
    SCRAPING = Scraping


config = Config()
