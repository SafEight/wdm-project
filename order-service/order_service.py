from urllib import request
from order import Order
import redis
import os
import requests
import uuid


DB = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
    db=int(os.environ["REDIS_DB"]),
    decode_responses=True,
)


class OrderServiceFunctions:
    functions = {}

    @classmethod
    def register(cls, name):
        def inner(func):
            cls.functions[name] = func
            return func

        return inner


class OrderService:
    def __init__(self):
        self.db: redis.Redis = DB

    def close_db_connection(self):
        self.db.close()

    @OrderServiceFunctions.register("create_order")
    def create_order(self, user_id=None):
        order_id = str(uuid.uuid4())
        o = Order(order_id, user_id, False, [], 0)
        self.db.set(o.order_id, o.toJSON())
        return True, o.toJSON()

    @OrderServiceFunctions.register("remove_order")
    def remove_order(self, order_id=None):
        self.db.delete(order_id)
        return True, f"Deleted order {order_id}!"

    @OrderServiceFunctions.register("add_item")
    def add_item(self, order_id=None, item_id=None):
        pipe = self.db.pipeline()
        while True:
            try:
                pipe.watch(order_id)
                order_json = pipe.get(order_id)

                if not order_json:
                    pipe.unwatch()
                    return False, "Order does not exist!"

                o = Order.fromJSON(order_json)
                if not o.add_item(item_id):
                    pipe.unwatch()
                    return False, "Item does not exist!"

                pipe.multi()
                pipe.set(o.order_id, o.toJSON())
                pipe.execute()
                return True, f"Added item!: {item_id}"
            except redis.WatchError:
                continue

    @OrderServiceFunctions.register("remove_item")
    def remove_item(self, order_id=None, item_id=None):
        pipe = self.db.pipeline()
        while True:
            try:
                pipe.watch(order_id)
                order_json = pipe.get(order_id)

                if not order_json:
                    pipe.unwatch()
                    return False, "Order does not exist!"

                o = Order.fromJSON(order_json)

                if o.paid:
                    pipe.unwatch()
                    return False, "Order is already paid!"

                if not o.remove_item(item_id):
                    pipe.unwatch()
                    return False, "Item does not exist!"

                pipe.multi()
                pipe.set(o.order_id, o.toJSON())
                pipe.execute()
                return True, f"Removed item!: {item_id}"
            except redis.WatchError:
                continue

    @OrderServiceFunctions.register("find_order")
    def find_order(self, order_id=None):
        order_json = self.db.get(order_id)

        if not order_json:
            return False, "Order does not exist!"

        o = Order.fromJSON(order_json)
        return True, o.toJSON()

    @OrderServiceFunctions.register("checkout")
    def checkout(self, order_id=None):
        order_json = self.db.get(order_id)

        if not order_json:
            return False, "Order does not exist!"

        o = Order.fromJSON(order_json)

        return self.checkout_stock_first(o)

    def checkout_stock_first(self, order):
        # subtract stock
        stockService = os.environ["STOCK_SERVICE"]
        subtract_all = f"{stockService}/subtract_all"
        subtract_all_data = {"items": order.items}
        subtract_all_response = requests.post(subtract_all, json=subtract_all_data)
        # print(f"subtract_all_response: {subtract_all_response.status_code}", flush=True)
        # print(
        #     f"subtract_all_response content: {subtract_all_response.json()}",
        #     flush=True,
        # )
        if subtract_all_response.status_code >= 400:
            return False, subtract_all_response.json()

        order.total_cost = subtract_all_response.json()["total_cost"]

        # pay for order
        paymentService = os.environ["PAYMENT_SERVICE"]

        pay = (
            f"{paymentService}/pay/{order.user_id}/{order.order_id}/{order.total_cost}"
        )
        pay_response = requests.post(pay)
        # print(f"pay_response: {pay_response}", flush=True)
        # print(f"pay_response: {pay_response.content}", flush=True)
        if pay_response.status_code >= 400:
            # rollback stock subtractions
            add_all = f"{stockService}/add_all"
            add_all_data = {"items": order.items}
            add_all_response = requests.post(add_all, json=add_all_data)
            if add_all_response.status_code >= 400:
                return False, add_all_response.json()

            return False, pay_response.text

        return True, "Successful order!"

    # def checkout(self, order_id):
    #     order_json = self.db.get(order_id)

    #     if not order_json:
    #         return False, "Order does not exist!"

    #     o = Order.fromJSON(order_json)

    #     if o.paid:
    #         return False, "Order is already paid!"

    #     o.paid = True
    #     self.db.set(o.order_id, o.toJSON())
    #     return True, f"Order {order_id} paid!"
