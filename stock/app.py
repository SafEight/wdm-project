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
    
@app.post('/add_all')
def add_all_stock():
    items = request.json["items"]
    for item in items:
        added = stock.add(item, 1)
        if not added:
            return jsonify({"error": f"Item {item} not found!"}), 400
    return "All items added!", 200

@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    removed, _ = stock.subtract(item_id, amount)
    if removed:
        return jsonify({"msg": "Stock removed"}), 200
    else:
        return jsonify({"error": "Insufficient stock or item not found!"}), 400

@app.post('/subtract_all')
def remove_all_stock():
    items = request.json["items"]
    subtracted_items = []
    total_cost = 0
    for item in items:
        removed, price = stock.subtract(item, 1)

        if not removed:
            # Rollback subtractions
            for sub_item in subtracted_items:
                add_stock(sub_item, 1)

            return jsonify({"error": f"Insufficient stock or item not found! Item id: {item}."}), 400
        
        total_cost += price
        subtracted_items.append(item)
    
    return jsonify({"total_cost": total_cost}), 200