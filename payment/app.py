import os
import atexit, uuid

from flask import Flask, jsonify

app = Flask("payment-service")

@app.get("/")
def status():
    data = {
        "msg": "Success /payment is online"
    }
    return jsonify(data), 200


@app.post("/create_user")
def create_user():
    return 0

@app.get("/find_user/<user_id>")
def find_user(user_id: str):
    return 0

@app.post("/add_funds/<user_id>/<amount>")
def add_credit(user_id: str, amount: int):
    return 0

@app.post("/pay/<user_id>/<order_id>/<amount>")
def remove_credit(user_id: str, order_id: str, amount: int):
    return 0

@app.post("/cancel/<user_id>/<order_id>")
def cancel_payment(user_id: str, order_id: str):
    return 0

@app.post("/status/<user_id>/<order_id>")
def payment_status(user_id: str, order_id: str):
    return 0