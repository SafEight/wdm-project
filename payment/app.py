import os
import atexit, uuid

from flask import Flask, jsonify
import redis


app = Flask("payment-service")

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))


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
    db.set(f"user:{user_id}", 0)
    return jsonify({"user_id": user_id}), 200

@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    # returns the user information
    user_credit = db.get(f"user:{user_id}")
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user_id": user_id, "credit": int(user_credit)}), 200

@app.post('/add_funds/<user_id>/<amount>')
def add_credit(user_id: str, amount: int):
    # adds funds (amount) to the user’s (user_id) account
    user_credit = db.get(f"user:{user_id}")
    if user_credit is None:
        return jsonify({"error": "User not found"}), 404
    else:
        db.incrby(f"user:{user_id}", amount)
        return jsonify({"msg": "Funds added"}), 200

@app.post('/pay/<user_id>/<order_id>/<amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    # subtracts the amount of the order from the user’s credit (returns failure if credit is not enough)
    with db.lock(user_id):
        user_credit = db.get(f"user:{user_id}")
        if user_credit is None:
            return jsonify({"error": "User not found"}), 404
        user_credit = int(user_credit)
        if user_credit < amount:
            return jsonify({"error": "Insufficient credit"}), 400
        db.decrby(f"user:{user_id}", amount)
        return jsonify({"msg": "Payment successful"}), 200

@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    # cancels payment made by a specific user for a specific order.
    payment = db.get(f"payment:{user_id}:{order_id}")
    if payment is None:
        return jsonify({"error": "Payment not found"}), 404
    db.delete(f"payment:{user_id}:{order_id}")
    return jsonify({"msg": "Payment cancelled"}), 200

@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):
    # returns the status of the payment (paid or not)
    payment_made = db.get(f"payment:{user_id}:{order_id}")
    if payment_made is not None:
        return jsonify({"paid": True}), 200
    else:
        return jsonify({"paid": False}), 200