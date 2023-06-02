import pika
import sys
from message import Message
import os

host = os.environ["RMQ_HOST"]


class Sender:
    def __init__(self, host: str, queue_name: str):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def send_message(self, message: Message):
        try:
            self.channel.basic_publish(
                exchange="", routing_key=self.queue_name, body=message.toJson()
            )
            return True
        except Exception as e:
            print("Error while sending message: {}".format(e))
            return False
