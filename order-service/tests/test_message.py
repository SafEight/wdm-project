from message import Message
import uuid
import pytest


@pytest.fixture
def message():
    return Message(
        server_id="1",
        request_id=str(uuid.uuid4()),
        method_name="create_order",
        params={"order_id": "1"},
    )


def test_message_to_json(message):
    assert (
        message.toJson()
        == '{"server_id": "1", "request_id": "'
        + message.request_id
        + '", "method_name": "create_order", "params": {"order_id": "1"}}'
    )


def test_message_from_json(message):
    message_json = message.toJson()
    message2 = Message.fromJson(message_json)
    assert message2.toJson() == message_json


def test_get_method_name(message):
    assert message.method_name == "create_order"
