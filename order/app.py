import os
import atexit
import requests

from flask import Flask, jsonify
import redis
from orders import Order, order_from_JSON

gateway_url = os.environ['GATEWAY_URL']

app = Flask("order-service")

db: redis.Redis = redis.Redis(host=os.environ['REDIS_HOST'],
                              port=int(os.environ['REDIS_PORT']),
                              password=os.environ['REDIS_PASSWORD'],
                              db=int(os.environ['REDIS_DB']))

paymentService = os.environ['PAYMENT_SERVICE']
stockService = os.environ['STOCK_SERVICE']


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
    if not order_json:
        return "Order does not exist!", 400
    
    o = order_from_JSON(order_json)
    if not o.add_item(item_id):
        return "Item does not exist!", 400
    
    db.set(o.order_id, o.toJSON())
    return f"Added item!: {item_id}", 200


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

    # check if order exists
    order_json = db.get(order_id)
    if not order_json:
        return "Order does not exist!", 400
    
    order = order_from_JSON(order_json)

    return checkout_stock_first(order)
    # return checkout_payment_first(order)

def checkout_stock_first(order):
    # subtract stock
    subtractedItems = []
    stockService = os.environ['STOCK_SERVICE']
    for item in order.items:
        # stockService = ""
        subtract=f"{stockService}/subtract/{item}/1"
        subtract_response = requests.post(subtract)

        if subtract_response.status_code >= 400:

            # rollback stock subtractions
            for subtractedItem in subtractedItems:
       
                add=f"{stockService}/add/{subtractedItem}/1"
                add_response = requests.post(add)
                if add_response.status_code >= 400:
                    
                    return f"Fatal error: {add_response}", 500
            return subtract_response.json(), subtract_response.status_code
        
        subtractedItems.append(item)
    
    # pay for order
    # paymentService = ""
    paymentService = os.environ['PAYMENT_SERVICE']

    pay=f"{paymentService}/pay/{order.user_id}/{order.order_id}/{order.total_cost}"
    pay_response = requests.post(pay)
    if pay_response.status_code >= 400:

        #rollback stock subtractions
        for item in order.items:
            stockService = os.environ['STOCK_SERVICE']
            add=f"{stockService}/add/{item}/1"
            add_response = requests.post(add)
            if add_response.status_code >= 400:
                return f"Fatal error: {add_response}", 500

        return pay_response.json(), pay_response.status_code
    
    return "Successful order!", 200

def checkout_payment_first(order):

    # pay for order
    pay=f"{paymentService}/pay/{order.user_id}/{order.order_id}/{order.total_cost}"
    pay_response = requests.post(pay).json()
    if pay_response.status_code >= 400:
        return pay_response

    # subtract stock
    subtractedItems = []
    for item in order.items:
        subtract=f"{stockService}/subtract/{item}/1"
        subtract_response = requests.post(subtract).json()
        print("*************", flush=True)    
        print(order, flush=True)
        print("*************", flush=True)    
        print(subtract_response.json(), flush=True)
        print("*************", flush=True)
        if subtract_response.status_code >= 400:

            # cancel payment
            cancel=f"{paymentService}/cancel/{order.user_id}/{order.order_id}"
            cancel_response = requests.post(cancel
                                            ).json()
            if cancel_response.status_code >= 400:
                return f"Fatal error: {cancel_response}", 500

            # rollback stock subtractions
            for subtractedItem in subtractedItems:
                add=f"{stockService}/add/{subtractedItem}/1"
                add_response = requests.post(add).json()
                if add_response.status_code >= 400:
                    return f"Fatal error: {add_response}", 500
            
            return subtract_response
        
        subtractedItems.append(item)
    
    return "Successful order!", 200
