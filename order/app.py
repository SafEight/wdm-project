import uuid
import pika
import time

from flask import Flask, jsonify

app = Flask("order-service")
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

request_queue = "request_queue"
response_queue = "response_queue"

responses = {}

@app.get("/")
def status():
    data = {
        "msg": "Success orders/ is online"
    }
    return jsonify(data), 200

@app.post("/create/<user_id>")
def create_order(user_id): 
    return send_message_to_queue("/create/<user_id>", user_id)

@app.delete("/remove/<order_id>")
def remove_order(order_id):
    return send_message_to_queue("/remove/<order_id>", order_id)

@app.post("/addItem/<order_id>/<item_id>")
def add_item(order_id, item_id):
    return send_message_to_queue("/addItem/<order_id>/<item_id>", {order_id, item_id})

@app.delete("/removeItem/<order_id>/<item_id>")
def remove_item(order_id, item_id):
    return send_message_to_queue("removeItem/<order_id>/<item_id>", {order_id, item_id})

@app.get("/find/<order_id>")
def find_order(order_id):
    return send_message_to_queue("/find/<order_id>", order_id)

@app.post("/checkout/<order_id>")
def checkout(order_id):
    return send_message_to_queue("/checkout/<order_id>", order_id)

def send_message_to_queue(request_body):
    request_id = str(uuid.uuid4())

    channel.basic_publish(exchange="", routing_key=request_queue, body={request_id, request_body})

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