import os
import atexit
import json

from flask import Flask, jsonify, request
import redis
from stock import Stock


app = Flask("stock-service")

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))


def close_db_connection():
    db.close()


atexit.register(close_db_connection)

stock = Stock(db)

@app.get("/")
def status():
    data = {
        "msg": "Success stock is online"
    }
    return jsonify(data), 200


@app.post('/item/create/<price>')
def create_item(price: int):
    item_id = stock.create(price)
    return jsonify({"item_id": item_id}), 200


@app.get('/find/<item_id>')
def find_item(item_id: str):
    item = stock.find(item_id)
    if item:
        return jsonify(json.loads(item)), 200
    else:
        return jsonify({"error": "Item not found!"}), 400

@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    added = stock.add(item_id, amount)
    if added:
        return jsonify({"msg": "Stock added"}), 200
    else:
        return jsonify({"error": "Item not found!"}), 400


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    removed = stock.subtract(item_id, amount)
    if removed:
        return jsonify({"msg": "Stock removed"}), 200
    else:
        return jsonify({"error": "Insufficient stock or item not found!"}), 400