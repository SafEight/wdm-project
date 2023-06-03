from item import Item
import redis
import os
import uuid

DB = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
    db=int(os.environ["REDIS_DB"]),
)


class StockServiceFunctions:
    functions = {}

    @classmethod
    def register(cls, name):
        def inner(func):
            cls.functions[name] = func
            return func

        return inner


class StockService:
    def __init__(self):
        self.db: redis.Redis = DB

    def close_db_connection(self):
        self.db.close()

    @StockServiceFunctions.register("create_item")
    def create_item(self, price=None):
        item = Item(price)
        self.db.set(item.item_id, item.toJSON())
        return True, item.item_id

    @StockServiceFunctions.register("find_item")
    def find_item(self, item_id=None):
        item_json = self.db.get(item_id)
        if not item_id:
            return False, "Item not found!"
        return True, item_json

    @StockServiceFunctions.register("add_stock")
    def add_stock(self, item_id=None, amount=None):
        item_json = self.db.get(item_id)
        if not item_json:
            return False, "Item not found!"
        item = Item.fromJSON(item_json)
        item.add_amount(amount)
        self.db.set(item.item_id, item.toJSON())
        return True, "Stock added"

    @StockServiceFunctions.register("subtract_stock")
    def subtract_stock(self, item_id=None, amount=None):
        item_json = self.db.get(item_id)
        if not item_json:
            return False, "Item not found!"
        item = Item.fromJSON(item_json)
        subtracted = item.subtract_amount(amount)
        if not subtracted:
            return False, "Not enough stock!"
        self.db.set(item.item_id, item.toJSON())
        return True, "Stock subtracted"

    @StockServiceFunctions.register("add_all_stock")
    def add_all_stock(self, items=None):
        for item in items:
            added, msg = self.add_stock(item, 1)
            if not added:
                return False, msg
        return True, "All items added!"

    @StockServiceFunctions.register("subtract_all_stock")
    def subtract_all_stock(self, items=None):
        for item in items:
            subtracted, msg = self.subtract_stock(item, 1)
            if not subtracted:
                return False, msg
        return True, "All items subtracted!"
