import json
import uuid
import redis

class Stock:
    def __init__(self, db):
        self.db = db

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def find(self, item_id):
        item_data = self.db.get(item_id)
        if item_data:
            item = json.loads(item_data)
            return json.dumps({"item_id": item_id, "stock": item["amount"], "price": item["price"]})
        else:
            return None

    # This method might need to be updated if we want to do
    # different error handling (e.g. amount > item amount)    
    def subtract(self, item_id, amount):
        pipe = self.db.pipeline()
        while True:
            try:
                pipe.watch(item_id)
                item_data = pipe.get(item_id)
                if not item_data:
                    pipe.unwatch()
                    return False, 0
                item = json.loads(item_data)
                current_stock = item["amount"]
                if current_stock < int(amount):
                    pipe.unwatch()
                    return False, 0
                item["amount"] = current_stock - int(amount)
                pipe.multi()
                pipe.set(item_id, json.dumps(item))
                pipe.execute()
                return True, int(item["price"])
            except redis.WatchError:
                continue

    def add(self, item_id, amount):
        pipe = self.db.pipeline()
        while True:
            try:
                pipe.watch(item_id)
                item_data = pipe.get(item_id)
                if not item_data:
                    pipe.unwatch()
                    return False
                item = json.loads(item_data)
                item["amount"] += int(amount)
                pipe.multi()
                pipe.set(item_id, json.dumps(item))
                pipe.execute()
                return True
            except redis.WatchError:
                continue
        
    def create(self, price):
        item_id = str(uuid.uuid4())
        item = {"price": int(price), "amount": 0}
        self.db.set(item_id, json.dumps(item))
        return item_id