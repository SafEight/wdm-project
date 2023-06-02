from sender import Sender
from message import Message
import pytest
import uuid
import json


@pytest.fixture
def test_message():
    message = Message(
        server_id="1",
        request_id=str(uuid.uuid4()),
        method_name="create_order",
        params={"user_id": "1"},
    )
    return message


def test_sender_init():
    sender = Sender(host="localhost", queue_name="order_service")
    assert sender.queue_name == "order_service"
    assert sender.connection.is_open == True
    assert sender.channel.is_open == True


def test_sender_send_message(test_message):
    sender = Sender(host="localhost", queue_name="order_service")
    assert sender.send_message(test_message) == True
