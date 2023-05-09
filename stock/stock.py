import json
import uuid

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
        item_data = self.db.get(item_id)
        if item_data:
            with self.db.lock(item_id):
                item = json.loads(item_data)
                current_stock = item["amount"]
                if current_stock >= int(amount):
                    item["amount"] = current_stock - int(amount)
                    self.db.set(item_id, json.dumps(item))
                    return True
                else:
                    return False
        else:
            return False

    def add(self, item_id, amount):
        item_data = self.db.get(item_id)
        if item_data:
            item = json.loads(item_data)
            item["amount"] += int(amount)
            self.db.set(item_id, json.dumps(item))
            return True
        else:
            return False

    def create(self, price):
        item_id = str(uuid.uuid4())
        item = {"price": price, "amount": 0}
        self.db.set(item_id, json.dumps(item))
        return item_id