import json
import uuid


class Item:
    def __init__(self, item_id, price, stock):
        self.item_id = item_id
        self.price = int(price)
        self.stock = int(stock)

    def toJSON(self):
        return json.dumps(self.__dict__)

    def add_stock(self, stock):
        self.stock += int(stock)
        return True

    def subtract_stock(self, stock):
        try:
            if self.stock - stock < 0:
                return False
            self.stock -= stock
            return True
        except ValueError as ve:
            return False

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Item):
            return self.item_id == __o.item_id

    @staticmethod
    def fromJSON(json_string):
        json_dict = json.loads(json_string)
        item = Item(**json_dict)
        return item
