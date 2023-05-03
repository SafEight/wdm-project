import os
import atexit

from flask import Flask, jsonify, request
import redis


app = Flask("stock-service")

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))


def close_db_connection():
    db.close()


atexit.register(close_db_connection)

@app.get("/")
def status():
    data = {
        "msg": "Success stock is online"
    }
    return jsonify(data)


@app.post('/item/create/<price>')
def create_item(price: int):
    pass


@app.get('/find/<item_id>')
def find_item(item_id: str):
    pass


@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):
    pass


@app.post('/subtract/<item_id>/<amount>')
def remove_stock(item_id: str, amount: int):
    pass
