from item import Item
import redis
import os
import uuid
import json

DB = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
    db=int(os.environ["REDIS_DB"]),
    decode_responses=True,
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
        item_id = str(uuid.uuid4())
        item = Item(item_id, price, 0)
        self.db.set(item.item_id, item.toJSON())
        return True, item.toJSON()

    @StockServiceFunctions.register("find_item")
    def find_item(self, item_id=None):
        item_json = self.db.get(item_id)
        print(item_json, flush=True)
        if not item_id:
            return False, "Item not found!"
        return True, item_json

    @StockServiceFunctions.register("add_stock")
    def add_stock(self, item_id=None, amount=None):
        amount = int(amount)
        item_json = self.db.get(item_id)
        if not item_json:
            return False, "Item not found!"
        item = Item.fromJSON(item_json)
        item.add_stock(amount)
        self.db.set(item.item_id, item.toJSON())
        return True, "Stock added"

    @StockServiceFunctions.register("subtract_stock")
    def subtract_stock(self, item_id=None, amount=None):
        amount = int(amount)
        item_json = self.db.get(item_id)
        if not item_json:
            return False, "Item not found!"
        item = Item.fromJSON(item_json)
        subtracted = item.subtract_stock(amount)
        if not subtracted:
            return False, "Not enough stock!"
        self.db.set(item.item_id, item.toJSON())
        return True, "Subtracted stock!"

    @StockServiceFunctions.register("add_all_stock")
    def add_all_stock(self, items=None):
        for item in items:
            added, msg = self.add_stock(item, 1)
            if not added:
                return False, msg
        return True, "All items added!"

    @StockServiceFunctions.register("subtract_all_stock")
    def subtract_all_stock(self, items=None):
        subtracted_items = []
        total_cost = 0
        for item in items:
            removed, price = self.subtract_one_stock(item, 1)
            if not removed:
                for sub_item in subtracted_items:
                    self.add_stock(sub_item, 1)
                return False, json.dumps(
                    {"error": f"Insufficient stock or item not found! Item id: {item}."}
                )

            subtracted_items.append(item)
            total_cost += price
        return True, json.dumps({"total_cost": total_cost})

    def subtract_one_stock(self, item_id=None, amount=None):
        amount = int(amount)
        item_json = self.db.get(item_id)
        if not item_json:
            return False, "Item not found!"
        item = Item.fromJSON(item_json)
        subtracted = item.subtract_stock(amount)
        if not subtracted:
            return False, "Not enough stock!"
        self.db.set(item.item_id, item.toJSON())
        return True, item.price
