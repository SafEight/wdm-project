import uuid
import aio_pika
import asyncio
import time
import json
import os
from connection import QueueHandler
from http import HTTPStatus
from quart import Quart, make_response, jsonify, request

host = os.environ["RMQ_HOST"]

app = Quart("stock-service")
outgoing_queue = "stock_service"
server_id = str(uuid.uuid4())
loop = asyncio.get_running_loop()
queue_handler = QueueHandler(server_id, outgoing_queue)


@app.get("/")
def status():
    data = {"msg": "Success stock/ is online"}
    return jsonify(data), 200


@app.post("/item/create/<price>")
async def create_item(price: int):
    req_body = {
        "server_id": server_id,
        "method_name": "create_item",
        "params": {"price": price},
    }
    return await send_message_to_queue(request_body=req_body)


@app.get("/find/<item_id>")
async def find_item(item_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "find_item",
        "params": {"item_id": item_id},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/add/<item_id>/<amount>")
async def add_funds(item_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "add_stock",
        "params": {"item_id": item_id, "amount": amount},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/add_all")
async def add_all_stock():
    items = await request.get_json()
    req_body = {
        "server_id": server_id,
        "method_name": "add_all_stock",
        "params": {"items": items["items"]},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/subtract/<item_id>/<amount>")
async def remove_stock(item_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "subtract_stock",
        "params": {"item_id": item_id, "amount": amount},
    }
    return await send_message_to_queue(request_body=req_body)


@app.post("/subtract_all")
async def remove_all_stock():
    items = await request.get_json()
    req_body = {
        "server_id": server_id,
        "method_name": "subtract_all_stock",
        "params": {"items": items["items"]},
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
