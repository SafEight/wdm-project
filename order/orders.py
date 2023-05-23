import uuid
import json
import requests
import os

class Order:

    def __init__(self, user_id):
        self.order_id = str(uuid.uuid4())
        self.paid = False
        self.items = [] # making this a dictionary could reduce the number of calls between services when adding repeated items
        self.user_id = user_id
        self.total_cost = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def add_item(self, item_id):
        self.items.append(item_id)
        return True

    def remove_item(self, item_id):
        try:
            self.items.remove(item_id)
            return True
        except ValueError as ve:
            return False

    def pay(self):
        self.paid = True

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Order):
            return self.order_id == __o.order_id


def order_from_JSON(json_string):
    json_dict = json.loads(json_string)
    order = Order(json_dict['user_id'])
    order.order_id = json_dict['order_id']
    order.paid = json_dict['paid']
    order.items = json_dict['items']
    order.total_cost = json_dict['total_cost']
    return order
