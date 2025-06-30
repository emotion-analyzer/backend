import os

from dotenv import load_dotenv

load_dotenv(os.getenv(key="APP_ENV", default="test.env"))

class Analyzer:
    """Analyzer configuration."""
    URL = os.getenv("ANALYZER_BASE_URL")

class Scraper:
    """Scraper configuration."""
    URL = os.getenv("SCRAPER_BASE_URL")

class Httpx:
    """Httpx configuration."""
    CONNECTION_TIMEOUT = float(os.getenv("HTTPX_CONNECTION_TIMEOUT", 15))

class Config:
    """Represents configuration state in the application.

    Import in your module and access (after setting in the proper .env).
    """
    ANALYZER = Analyzer
    SCRAPER = Scraper
    HTTPX = Httpx

config = Config()
