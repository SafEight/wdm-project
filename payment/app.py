import time
import uuid
import pika

from flask import Flask, jsonify

app = Flask("payment-service")
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

request_queue = "request_queue"
response_queue = "response_queue"

responses = {}

@app.get("/")
def status():
    data = {
        "msg": "Success /payment is online"
    }
    return jsonify(data), 200


@app.post("/create_user")
def create_user():
    return send_message_to_queue("/create_user", None)

@app.get("/find_user/<user_id>")
def find_user(user_id: str):
    return send_message_to_queue("/find_user/<user_id>", user_id)

@app.post("/add_funds/<user_id>/<amount>")
def add_credit(user_id: str, amount: int):
    return send_message_to_queue("/add_funds/<user_id>/<amount>", {user_id, amount})

@app.post("/pay/<user_id>/<order_id>/<amount>")
def remove_credit(user_id: str, order_id: str, amount: int):
    return send_message_to_queue("pay/<user_id>/<order_id>/<amount>", {user_id, order_id, amount})

@app.post("/cancel/<user_id>/<order_id>")
def cancel_payment(user_id: str, order_id: str):
    return send_message_to_queue("/cancel/<user_id>/<order_id>", {user_id, order_id})

@app.post("/status/<user_id>/<order_id>")
def payment_status(user_id: str, order_id: str):
    return send_message_to_queue("/status/<user_id>/<order_id>", {user_id, order_id})

def send_message_to_queue(request_body):
    request_id = str(uuid.uuid4())

    channel.basic_publish(exchange='', routing_key=request_queue, body={request_id, request_body})

    response = wait_for_response(request_id)

    if response:
        return jsonify(response)
    else:
        return jsonify({'error': 'Timeout occurred'}), 500

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