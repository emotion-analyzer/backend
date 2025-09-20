
from aio_pika import Message
from util.codes import EOF
from util.schemas import EndOfPosts, QueueMessage

from query_processor.core.util import done_receiving_messages
from query_processor.tests.test_constants import analysis_result_body


def test_message_with_wrong_code_returns_none():
    body = QueueMessage(query_processor_id="id1", code=10)
    message=  Message(body=body.model_dump_json().encode('utf-8'))
    assert done_receiving_messages(message, [], None) is None

def test_analysis_result_returns_none_if_no_eof_has_been_received():
    message= Message(body=analysis_result_body.model_dump_json().encode('utf-8'))
    analysis_results = []
    assert done_receiving_messages(message, analysis_results , None) is None

def test_eof_returns_total_if_no_messages_have_been_received():
    body = EndOfPosts(query_processor_id="id1", code=EOF, total=10)
    message= Message(body=body.model_dump_json().encode('utf-8'))
    analysis_results = []
    assert done_receiving_messages(message, analysis_results , None) == 10

def test_analysis_result_returns_messages_left_if_eof_has_been_received():
    eof_body = EndOfPosts(query_processor_id="id1", code=EOF, total=10)
    message= Message(body=eof_body.model_dump_json().encode('utf-8'))
    analysis_results = []
    messages_left = done_receiving_messages(message, analysis_results, None)
    message= Message(body=analysis_result_body.model_dump_json().encode('utf-8'))
    assert done_receiving_messages(message, analysis_results , messages_left) == 9


def test_analysis_result_returns_messages_left_if_eof_received_before():
    analysis_results = []
    messages_left = None
    message = Message(body=analysis_result_body.model_dump_json().encode('utf-8'))
    messages_left = done_receiving_messages(message, analysis_results, messages_left)
    eof_body = EndOfPosts(query_processor_id="id1", code=EOF, total=10)
    message = Message(body=eof_body.model_dump_json().encode('utf-8'))
    messages_left = done_receiving_messages(message, analysis_results, messages_left)
    message = Message(body=analysis_result_body.model_dump_json().encode('utf-8'))
    assert done_receiving_messages(message, analysis_results , messages_left) == 8
