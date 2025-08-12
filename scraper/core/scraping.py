from abc import abstractmethod
from dataclasses import dataclass

from aio_pika import DeliveryMode, Message
from scraper.config import config
from scraper.core.queue_middleware import send_message
from scraper.core.schemas import FetchQuery, Post


@dataclass
class Scraper:
    """Scraper base class."""

    def __init__(self, name, channel):
        """Scraper constructor."""
        self._name = name
        self.channel = channel

    @abstractmethod
    def query(self, query: FetchQuery, query_processor_id: str):
        """Search for posts according to the fetch request details."""

    async def send_to_analyzer(self, post:Post):
        """Send post to analyzer."""
        message = Message(post.model_dump_json().encode('utf-8'),
                          delivery_mode=DeliveryMode.NOT_PERSISTENT)
        await send_message(message, self.channel, config)

    def get_name(self) -> str:
        """Return scraper's associated social network ."""
        return self._name
