from time import sleep
from sender import Sender
import pika
import redis
import os
from order_service import OrderService, OrderServiceFunctions

from message import Message

host = os.environ["RMQ_HOST"]


class Consumer:
    def __init__(self):
        self.queue_name = "order_service"
        print(f"Connecting to rabbitmq: {host} ", flush=True)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.order_service = OrderService()
        self.sender = Sender(host=host, queue_name=self.queue_name)

    def callback(self, ch, method, properties, body):
        message = Message.fromJson(body)
        self.handle_message(message)

    def handle_message(self, message: Message):
        print(f"(Handling message: {message.toJson()}")
        method_name = message.method_name

        if method_name not in OrderServiceFunctions.functions:
            raise Exception("Method not found")

        print(method_name, flush=True)

        func = getattr(OrderService, method_name)
        res, message = func(self.order_service, **message.params)


if __name__ == "__main__":
    consumer = Consumer()
    consumer.channel.basic_consume(
        queue=consumer.queue_name, on_message_callback=consumer.callback, auto_ack=True
    )
    print(" [*] Waiting for messages. To exit press CTRL+C")
    consumer.channel.start_consuming()
