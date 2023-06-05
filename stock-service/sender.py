import pika
import sys
from message import OutgoingMessage
import os

host = os.environ["RMQ_HOST"]


class Sender:
    def __init__(self, host: str, queue_name: str):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, heartbeat=0)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def send_message(self, outgoing_message: OutgoingMessage):
        try:
            print("Sending message: {}".format(outgoing_message.toJson()), flush=True)
            self.channel.basic_publish(
                exchange="",
                routing_key=outgoing_message.server_id,
                body=outgoing_message.toJson(),
            )
            return True
        except Exception as e:
            print("Error while sending message: {}".format(e), flush=True)
            return False
