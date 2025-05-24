class ScraperError(Exception):
    """Raised if there was an issue when making the scraping request."""

    def __init__(self, code: int, scraper_name: str):
        self.code = code
        self.message = f"Error en scraper de {scraper_name}."
        super().__init__(self.message)

