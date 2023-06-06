from time import sleep
from sender import Sender
import pika
import os
from stock_service import StockService, StockServiceFunctions
from message import Message, OutgoingMessage

host = os.environ["RMQ_HOST"]


class Consumer:
    def __init__(
        self,
        queue_name,
        host,
        output_queue_name,
        ServiceClass,
        ServiceFunctions,
    ):
        self.queue_name = queue_name
        self.output_queue_name = output_queue_name
        self.host = host
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host)
                )
                print("========= RABBITMQ CONNECTED ==========", flush=True)
                break
            except:
                sleep(5)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.service = ServiceClass()
        self.sender = Sender(host=host, queue_name=self.output_queue_name)
        self.ServiceFunctions = ServiceFunctions
        # print(
        #     f"Connecting to rabbitmq: {host}, IncomingQueue: {self.queue_name}, OutgoingQueue: {self.output_queue_name}, Using Service: {self.service.__class__.__name__}, Using ServiceFunctions: {self.ServiceFunctions.__name__}",
        #     flush=True,
        # )

    def callback(self, ch, method, properties, body):
        message = Message.fromJson(body)
        self.handle_message(message)

    def handle_message(self, message: Message):
        # print(f"Handling message: {message.toJson()}")
        method_name = message.method_name

        if method_name not in self.ServiceFunctions.functions:
            raise Exception("Method not found")

        # print(method_name, flush=True)

        func = getattr(self.service.__class__, method_name)
        bool_res, res = func(self.service, **message.params)
        outgoing_message = OutgoingMessage(
            server_id=message.server_id,
            request_id=message.request_id,
            bool_result=bool_res,
            result=res,
        )
        self.sender.send_message(outgoing_message)


if __name__ == "__main__":
    consumer = Consumer(
        queue_name="stock_service",
        output_queue_name="stock_proxy",
        host=host,
        ServiceClass=StockService,
        ServiceFunctions=StockServiceFunctions,
    )
    consumer.channel.basic_consume(
        queue=consumer.queue_name, on_message_callback=consumer.callback, auto_ack=True
    )
    # print("[*] Waiting for messages. To exit press CTRL+C")
    consumer.channel.start_consuming()
