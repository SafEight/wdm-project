import json

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
            item = json.loads(item_data)
            current_stock = item["amount"]
            if current_stock >= amount:
                item["amount"] = current_stock - amount
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
            item["amount"] += amount
            self.db.set(item_id, json.dumps(item))
        else:
            return False

    def create(self, price):
        item_id = self.generate_item_id()
        item = {"price": price, "amount": 0}
        self.db.set(item_id, json.dumps(item))
        return item_id

    # Temp method to generate item IDs, this might be handled by db
    def generate_item_id(self):
        keys = self.db.keys()
        if len(keys) == 0:
            return 1
        else:
            item_amount = max(keys)
            return item_amount + 1