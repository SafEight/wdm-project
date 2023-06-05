import uuid
import aio_pika
import asyncio
import time
import json
import os
from connection import QueueHandler
from http import HTTPStatus
from quart import Quart, make_response, jsonify

host = os.environ["RMQ_HOST"]


app = Quart("payment-service")
outgoing_queue = "payment_service"
server_id = str(uuid.uuid4())
loop = asyncio.get_running_loop()
queue_handler = QueueHandler(server_id, outgoing_queue)


@app.get("/")
def status():
    data = {"msg": "Success payment/ is online"}
    return jsonify(data), 200


@app.post("/create_user")
async def create_user():
    req_body = {"server_id": server_id, "method_name": "create_user", "params": ""}
    return await send_message_to_queue(request_body=req_body)


@app.get("/find_user/<user_id>")
async def find_user(user_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "find_user",
        "params": {"user_id": user_id},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/add_funds/<user_id>/<amount>")
async def add_funds(user_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "add_funds",
        "params": {"user_id": user_id, "amount": amount},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/pay/<user_id>/<order_id>/<amount>")
async def remove_credit(user_id: str, order_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "pay",
        "params": {"user_id": user_id, "order_id": order_id, "amount": amount},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/cancel/<user_id>/<order_id>")
async def cancel_payment(user_id: str, order_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "cancel_payment",
        "params": {"user_id": user_id, "order_id": order_id},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/status/<user_id>/<order_id>")
async def payment_status(user_id: str, order_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "payment_status",
        "params": {"user_id": user_id, "order_id": order_id},
    }
    return await send_message_to_queue(request_body=req_body)


async def send_message_to_queue(request_body):
    request_id = str(uuid.uuid4())
    print(f"Sending request {request_id}")
    print(f"with server id {server_id}")
    request_body["request_id"] = request_id
    await queue_handler.connect()
    await queue_handler.channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(request_body).encode()),
        routing_key=outgoing_queue,
    )
    response = await wait_for_response(request_id)
    print(f"Response for request {request_id} received: {response}", flush=True)
    if response:
        return response
    else:
        return await make_response("No response", HTTPStatus.INTERNAL_SERVER_ERROR)


async def wait_for_response(request_id):
    start_time = time.time()
    timeout = 0.35
    print("this is still ok")
    while time.time() - start_time < timeout:
        if request_id in queue_handler.responses:
            (bool_result, result) = queue_handler.responses.pop(request_id)
            if bool_result:
                return await make_response(result, HTTPStatus.OK)
            else:
                return await make_response(result, HTTPStatus.BAD_REQUEST)
        await asyncio.sleep(0.01)

    return None
