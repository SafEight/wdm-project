import uuid
import pika
import time
import json
import os
from flask import Flask, jsonify

host = os.environ["RMQ_HOST"]


app = Flask("payment-service")
connection = pika.BlockingConnection(pika.ConnectionParameters(host))
channel = connection.channel()

request_queue = "payment_service"
response_queue = "payment_proxy"

server_id = str(uuid.uuid4())

responses = {}


@app.get("/")
def status():
    data = {"msg": "Success payment/ is online"}
    return jsonify(data), 200


@app.post("/create_user")
def create_user():
    req_body = {"server_id": server_id, "method_name": "create_user", "params": ""}
    return send_message_to_queue(request_body=req_body)


@app.get("/find_user/<user_id>")
def find_user(user_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "find_user",
        "params": {"user_id": user_id},
    }
    return send_message_to_queue(request_body=req_body)


@app.post("/add_funds/<user_id>/<amount>")
def add_credit(user_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "add_credit",
        "params": {"user_id": user_id, "amount": amount},
    }
    return send_message_to_queue(request_body=req_body)


@app.post("/pay/<user_id>/<order_id>/<amount>")
def remove_credit(user_id: str, order_id: str, amount: int):
    req_body = {
        "server_id": server_id,
        "method_name": "remove_credit",
        "params": {"user_id": user_id, "order_id": order_id, "amount": amount},
    }
    return send_message_to_queue(request_body=req_body)


@app.post("/cancel/<user_id>/<order_id>")
def cancel_payment(user_id: str, order_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "cancel_payment",
        "params": {"user_id": user_id, "order_id": order_id},
    }
    return send_message_to_queue(request_body=req_body)


@app.post("/status/<user_id>/<order_id>")
def payment_status(user_id: str, order_id: str):
    req_body = {
        "server_id": server_id,
        "method_name": "payment_status",
        "params": {"user_id": user_id, "order_id": order_id},
    }
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
    request_id = body.decode()
    responses[request_id] = {"msg": "Succesful response"}

    channel.basic_ack(delivery_tag=method.delivery_tag)


channel.queue_declare(queue=response_queue)
channel.basic_consume(queue=response_queue, on_message_callback=handle_message)
