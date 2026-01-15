from abc import abstractmethod
from dataclasses import dataclass
import re

from aio_pika import DeliveryMode, Message
from util.queue_middleware import send_message
from util.schemas import AnalysisRequest, Post

from scraper.config import config


@dataclass
class Scraper:
    """Scraper base class. Import and implement scraping logic for your social network."""

    def __init__(self, name, channel, languages, logger):
        """Scraper constructor."""
        self._name = name
        self.channel = channel
        self.logger = logger
        self.languages = languages
        self.logger.info(f"{self._name} scraper initialized with "
                         f"{self.languages} support.")

    @abstractmethod
    def query(self, query: AnalysisRequest) -> int:
        """Search for posts using specified parameters. Return amount of posts fetched."""

    def normalize(self, text: str) -> str:
        """Normalize post URLs in the post."""
        text = re.sub(r'(?:https?://|www\.)\S+', '<URL>', text)
        return text

    def validate_query(self, query: AnalysisRequest) -> bool:
        """Validate query parameters (language only so far)."""
        if query.parameters.language not in self.languages:
            self.logger.warning(f"Unsupported language: {query.parameters.language}.")
            return False
        return True

    async def send_to_analyzer(self, post: Post):
        """Send post to analyzer."""
        message = Message(post.model_dump_json().encode('utf-8'),
                          delivery_mode=DeliveryMode.PERSISTENT)
        await send_message(self.channel.default_exchange, message,
                           config.RABBIT_MQ.SCRAPING_RESULT_QUEUE, self.logger)

    def get_name(self) -> str:
        """Return scraper's associated social network ."""
        return self._name
