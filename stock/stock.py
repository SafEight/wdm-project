import json
import uuid
from antidotedb import AntidoteClient, Key, Counter, Set, Map

class Stock:
    def __init__(self, db):
        self.db = db

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def find(self, item_id):
        tx = self.db.start_transaction()
        item_data = tx.read_objects(Key("stock", item_id, "MAP"))
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
        
        item = Key("stock", item_id, "MAP")
        price = Key("", "price", int(price))
        amount = Key("", "amount", 0)

        tx = self.db.start_transaction()
        tx.update_objects(Map.UpdateOp(item, [price, amount]))
        tx.commit()
        
        return item_id