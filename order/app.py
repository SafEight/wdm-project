import os
import atexit

from flask import Flask, jsonify
import redis
from orders import Order, order_from_JSON

gateway_url = os.environ['GATEWAY_URL']

app = Flask("order-service")

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))


def close_db_connection():
    db.close()


@app.get("/")
def status():
    data = {
        "msg": "Success orders/ is online"
    }
    return jsonify(data), 200


atexit.register(close_db_connection)


@app.post('/create/<user_id>')
def create_order(user_id):
    o = Order(user_id)
    db.set(o.order_id, o.toJSON())
    return jsonify({"order_id":  o.order_id}), 200


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    db.delete(order_id)
    return "", 200


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    order_json = db.get(order_id)
    if order_json:
        o = order_from_JSON(order_json)
        o.add_item(item_id)
        db.set(o.order_id, o.toJSON())
        return f"Added item!: {item_id}", 200
    return "Order does not exist!", 400


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    order_json = db.get(order_id)
    if order_json:
        o = order_from_JSON(order_json)
        o.remove_item(item_id)
        db.set(o.order_id, o.toJSON())
        return f"Removed item: {item_id}!", 200
    return "Order does not exist!", 400


@app.get('/find/<order_id>')
def find_order(order_id):
    order_json = db.get(order_id)
    if order_json:
        o = order_from_JSON(order_json)
        return o.toJSON(), 200
    return "Order does not exist!", 400


@app.post('/checkout/<order_id>')
def checkout(order_id):
    pass
