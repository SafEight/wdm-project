from order import Order
import redis
import os

DB = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
    db=int(os.environ["REDIS_DB"]),
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
        o = Order(user_id)
        self.db.set(o.order_id, o.toJSON())
        return True, o.order_id

    @OrderServiceFunctions.register("remove_order")
    def remove_order(self, order_id=None):
        self.db.delete(order_id)
        return True, f"Deleted order {order_id}!"

    @OrderServiceFunctions.register("add_item")
    def add_item(self, order_id=None, item_id=None):
        order_json = self.db.get(order_id)
        if not order_json:
            return False, "Order does not exist!"

        o = Order.fromJSON(order_json)
        if not o.add_item(item_id):
            return False, "Item does not exist!"

        self.db.set(o.order_id, o.toJSON())
        return True, f"Added item!: {item_id}"

    @OrderServiceFunctions.register("remove_item")
    def remove_item(self, order_id=None, item_id=None):
        order_json = self.db.get(order_id)

        if not order_json:
            return False, "Order does not exist!"

        o = Order.fromJSON(order_json)

        if o.paid:
            return False, "Order is already paid!"

        if not o.remove_item(item_id):
            return False, "Item does not exist!"

        self.db.set(o.order_id, o.toJSON())
        return True, f"Removed item!: {item_id}"

    @OrderServiceFunctions.register("find_order")
    def find_order(self, order_id=None):
        order_json = self.db.get(order_id)

        if not order_json:
            return False, "Order does not exist!"

        o = Order.fromJSON(order_json)
        return True, o.toJSON()

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
