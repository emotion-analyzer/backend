# ruff: noqa: T201
import json
from abc import abstractmethod
from dataclasses import dataclass

from scraper.config import config
from scraper.core.schemas import Post, EmotionalAnalysisParams
from scraper.core.queue_middleware import send_message
from aio_pika import DeliveryMode, Message


@dataclass
class Scraper:

    def __init__(self, name, channel):
        """Scraper base class."""
        self._name = name
        self.channel = channel

    @abstractmethod
    def query(self, query: EmotionalAnalysisParams) -> list[Post]:
        """Search for posts according to the fetch request details."""

    async def send_to_analyzer(self, post: Post):
        """Send post to analyzer."""
        message = Message(post.model_dump_json().encode('utf-8'),
                          delivery_mode=DeliveryMode.NOT_PERSISTENT)
        await send_message(message, self.channel, config)

    def get_name(self) -> str:
        return self._name