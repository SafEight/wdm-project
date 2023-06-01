import os
import atexit
import json

from flask import Flask, jsonify, request

app = Flask("stock-service")

@app.get("/")
def status():
    data = {
        "msg": "Success stock is online"
    }
    return jsonify(data), 200


@app.post('/item/create/<price>')
def create_item(price: int):
    return 0

@app.get('/find/<item_id>')
def find_item(item_id: str):
    return 0

@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    return 0    
    
@app.post('/add_all')
def add_all_stock():
    return 0

@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    return 0

@app.post('/subtract_all')
def remove_all_stock():
    return 0