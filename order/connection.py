import asyncio
import aio_pika
import os
from flask import Flask, jsonify
import json

host = os.environ["RMQ_HOST"]


class QueueHandler:
    def __init__(self, incoming_queue_name, outgoing_queue_name) -> None:
        self.responses = {}
        self.loop = asyncio.get_running_loop()
        self.incoming_queue = None
        self.incoming_queue_name = incoming_queue_name
        self.outgoing_queue = None
        self.outgoing_queue_name = outgoing_queue_name
        self.connection = None
        self.channel = None

    def is_ready(self):
        return self.connection is not None and self.connection.is_open

    async def connect(self):
        if self.connection is None or self.connection.is_closed:
            await self.create_connection()
        return self.connection

    async def start_consuming(self):
        await self.incoming_queue.consume(self.handle_message)

    async def handle_message(self, message):
        async with message.process():
            message = message.body.decode()
            # print("Received message: {}".format(message), flush=True)
            message = IncomingMessage.fromJson(message)
            # print(message.result, flush=True)
            self.responses[message.request_id] = (message.bool_result, message.result)
            return

    async def create_connection(self):
        self.connection = await aio_pika.connect_robust(
            f"amqp://guest:guest@{host}/", loop=self.loop
        )
        # print(f"Connected to rabbitmq {self.connection}", flush=True)
        self.channel = await self.connection.channel()
        self.outgoing_queue = await self.channel.declare_queue(self.outgoing_queue_name)
        self.incoming_queue = await self.channel.declare_queue(self.incoming_queue_name)
        await self.start_consuming()

    async def send_message(self, message):
        await self.outgoing_queue.publish(
            aio_pika.Message(body=json.dumps(message).encode())
        )


class IncomingMessage:
    def __init__(self, server_id: str, request_id: str, bool_result: bool, result: str):
        self.server_id = server_id
        self.request_id = request_id
        self.bool_result = bool_result
        self.result = result

    def toJson(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def fromJson(json_str: str):
        json_dict = json.loads(json_str)
        return IncomingMessage(**json_dict)

    class Result:
        def __init__(self, bool_result: bool, result: str):
            self.bool_result = bool_result
            self.result = result
