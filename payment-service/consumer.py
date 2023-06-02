from time import sleep
from sender import Sender
import pika
import os
from payment_service import PaymentService, PaymentServiceFunctions

from message import Message

host = os.environ["RMQ_HOST"]


class Consumer:
    def __init__(self):
        self.queue_name = "payment_service"
        print(f"Connecting to rabbitmq: {host} ", flush=True)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, retry_delay=5, connection_attempts=5))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.payment_service = PaymentService()
        self.sender = Sender(host=host, queue_name="payment_proxy")

    def callback(self, ch, method, properties, body):
        message = Message.fromJson(body)
        self.handle_message(message)

    def handle_message(self, message: Message):
        print(f"Handling message: {message.toJson()}")
        method_name = message.method_name

        if method_name not in PaymentServiceFunctions.functions:
            raise Exception("Method not found")

        print(method_name, flush=True)

        func = getattr(PaymentService, method_name)
        res, message = func(self.payment_service, **message.params)


if __name__ == "__main__":
    consumer = Consumer()
    consumer.channel.basic_consume(
        queue=consumer.queue_name, on_message_callback=consumer.callback, auto_ack=True
    )
    print(" [*] Waiting for messages. To exit press CTRL+C")
    consumer.channel.start_consuming()
