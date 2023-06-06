import os
import atexit, uuid
from flask import Flask, jsonify
from antidotedb import AntidoteClient, Key, Register, Counter, Flag

db = AntidoteClient('antidote-service', 8087)

app = Flask("payment-service")

def close_db_connection():
    db.close()

atexit.register(close_db_connection)

@app.get("/")
def status():
    return jsonify({"msg": "Success payment is online" })

@app.post('/create_user')
def create_user():
    # creates a user with 0 credit
    user_id = str(uuid.uuid4())
    key = Key("payment", user_id, "COUNTER")
    tx = db.start_transaction()
    tx.update_objects(Counter.IncOp(key, 0))
    tx.commit()
    return jsonify({"user_id": user_id}), 200

@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    # returns the user information
    key = Key("payment", user_id, "COUNTER")
    tx = db.start_transaction()
    user_credit = tx.read_objects(key)
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    else:
        user_credit = user_credit[0].value()
        return jsonify({"user_id": user_id, "credit": user_credit}), 200

@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    # adds funds (amount) to the user’s (user_id) account
    key = Key("payment", user_id, "COUNTER")
    tx = db.start_transaction()
    user_credit = tx.read_objects(key)
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    else:
        tx.update_objects(Counter.IncOp(key, amount))
        tx.commit()
        return jsonify({"msg": "Funds added"}), 200

@app.post('/pay/<user_id>/<order_id>/<amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    # subtracts the amount of the order from the user’s credit (returns failure if credit is not enough)
    key = Key("payment", user_id, "BCOUNTER")
    tx = db.start_transaction()
    user_credit = tx.read_objects(key)
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    if user_credit[0].value() < int(amount):
        return jsonify({"error": "Insufficient credit"}), 400
    tx.update_objects(Counter.IncOp(key, -amount))
    tx.commit()
    return jsonify({"msg": "Payment successful"}), 200


@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    # cancels payment made by a specific user for a specific order. TODO
    tx = db.start_transaction()
    key = Key("order", f"{user_id}:{order_id}", "FLAG_DW")
    payment = tx.read_objects(key)
    if payment is None:
        return jsonify({"error": "Payment not found"}), 404
    else:
        tx.update_objects(Flag.UpdateOp(key, False))
        tx.commit()
        return jsonify({"msg": "Payment cancelled"}), 200

@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):
    # returns the status of the payment (paid or not)
    payment_made = db.get(f"payment:{user_id}:{order_id}")
    if payment_made is not None:
        return jsonify({"paid": True}), 200
    else:
        return jsonify({"paid": False}), 200