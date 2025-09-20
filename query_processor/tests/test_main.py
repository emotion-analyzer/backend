from unittest.mock import AsyncMock, MagicMock

from aio_pika import Message
import pytest
from util.codes import ANALYSIS_REQUEST
from util.schemas import AnalysisRequest

from query_processor.core.util import queue_scrape_request
from query_processor.tests.test_constants import analysis_request_parameters


@pytest.mark.asyncio
async def test_queue_scrape_request_calls_publish():
    fake_exchange = AsyncMock()
    fake_queue = MagicMock()
    fake_queue.name = "posts"
    fake_app = MagicMock()
    fake_app.state.channel.default_exchange = fake_exchange
    fake_app.state.posts_queue = fake_queue
    await queue_scrape_request(analysis_request_parameters, "id1", fake_app)
    fake_exchange.publish.assert_awaited_once()
    args, kwargs = fake_exchange.publish.await_args
    message, = args
    analysis_request_body = Message(body = AnalysisRequest(query_processor_id="id1",
                                                           code=ANALYSIS_REQUEST,
                                                           parameters=analysis_request_parameters).model_dump_json(by_alias=True).encode('utf-8') )
    assert message.body == analysis_request_body.body
    assert kwargs["routing_key"] == fake_queue.name
