import os
import atexit
import requests

from flask import Flask, jsonify
from orders import Order, order_from_JSON

app = Flask("order-service")

@app.get("/")
def status():
    data = {
        "msg": "Success orders/ is online"
    }
    return jsonify(data), 200

@app.post('/create/<user_id>')
def create_order(user_id): 
    return 0

@app.delete('/remove/<order_id>')
def remove_order(order_id):
    return 0

@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    return 0

@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    return 0

@app.get('/find/<order_id>')
def find_order(order_id):
    return 0

@app.post('/checkout/<order_id>')
def checkout(order_id):
    return 0