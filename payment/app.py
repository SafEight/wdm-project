import os
import atexit, uuid

from flask import Flask, jsonify

app = Flask("payment-service")


@app.get("/")
def status():
    return jsonify({"msg": "Success payment is online"})


@app.post("/create_user")
def create_user():
    # creates a user with 0 credit
    user_id = str(uuid.uuid4())
    return jsonify({"user_id": user_id}), 200


@app.get("/find_user/<user_id>")
def find_user(user_id: str):
    # returns the user information
    user_credit = user_id
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user_id": user_id, "credit": int(user_credit)}), 200


@app.post("/add_funds/<user_id>/<amount>")
def add_credit(user_id: str, amount: int):
    # adds funds (amount) to the user’s (user_id) account
    user_credit = user_id
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    else:
        return jsonify({"msg": "Funds added"}), 200


@app.post("/pay/<user_id>/<order_id>/<amount>")
def remove_credit(user_id: str, order_id: str, amount: int):
    # subtracts the amount of the order from the user’s credit (returns failure if credit is not enough)
    user_credit = user_id
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    user_credit = int(user_credit)
    if user_credit < int(amount):
        return jsonify({"error": "Insufficient credit"}), 400
    return jsonify({"msg": "Payment successful"}), 200


@app.post("/cancel/<user_id>/<order_id>")
def cancel_payment(user_id: str, order_id: str):
    # cancels payment made by a specific user for a specific order.
    payment = user_id
    if payment is None:
        return jsonify({"error": "Payment not found"}), 404
    return jsonify({"msg": "Payment cancelled"}), 200


@app.post("/status/<user_id>/<order_id>")
def payment_status(user_id: str, order_id: str):
    # returns the status of the payment (paid or not)
    payment_made = user_id
    if payment_made is not None:
        return jsonify({"paid": True}), 200
    else:
        return jsonify({"paid": False}), 200
