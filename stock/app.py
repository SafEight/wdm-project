import uuid
import pika
import time
import json
import os
from flask import Flask, jsonify

host = os.environ["RMQ_HOST"]


app = Flask("stock-service")
connection = pika.BlockingConnection(pika.ConnectionParameters(host))
channel = connection.channel()

request_queue = "stock_service"
response_queue = "stock_proxy"

server_id = str(uuid.uuid4())

responses = {}


@app.get("/")
def status():
    data = {"msg": "Success stock/ is online"}
    return jsonify(data), 200


@app.post("/item/create/<price>")
def create_item(price: int):
    req_body = {
        "server_id": server_id,
        "method_name": "create_item",
        "params": {"price": price},
    }
    return send_message_to_queue(request_body=req_body)


@app.get("/find/<item_id>")
def find_item(item_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "find_item",
        "params": {"item_id": item_id},
    }
    return send_message_to_queue(request_body=req_body)


@app.post("/add/<item_id>/<amount>")
def add_stock(item_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "add_stock",
        "params": {"item_id": item_id, "amount": amount},
    }
    return send_message_to_queue(request_body=req_body)


@app.post("/add_all")
def add_all_stock():
    req_body = {"server_id": server_id, "method_name": "add_all_stock", "params": ""}
    return send_message_to_queue(request_body=req_body)


@app.post("/subtract/<item_id>/<amount>")
def remove_stock(item_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "remove_stock",
        "params": {"item_id": item_id, "amount": amount},
    }
    return send_message_to_queue(request_body=req_body)


@app.post("/subtract_all")
def remove_all_stock():
    req_body = {"server_id": server_id, "method_name": "remove_all_stock", "params": ""}
    return send_message_to_queue(request_body=req_body)


def send_message_to_queue(request_body):
    request_id = str(uuid.uuid4())
    request_body["request_id"] = request_id

    channel.basic_publish(
        exchange="", routing_key=request_queue, body=json.dumps(request_body)
    )

    response = wait_for_response(request_id)

    if response:
        return jsonify(response)
    else:
        return jsonify({"error": "Timeout occurred"}), 500


def wait_for_response(request_id):
    start_time = time.time()
    timeout = 0.35

    while time.time() - start_time < timeout:
        if request_id in responses:
            return responses.pop(request_id)

        time.sleep(0.01)

    return None


def handle_message(channel, method, properties, body):
    print("Received message: {}".format(body), flush=True)
    request_id = body.decode()
    print("Received response for request {}".format(request_id), flush=True)
    responses[request_id] = {"msg": "Succesful response"}

    channel.basic_ack(delivery_tag=method.delivery_tag)


channel.queue_declare(queue=response_queue)
channel.basic_consume(queue=response_queue, on_message_callback=handle_message)
channel.start_consuming()
