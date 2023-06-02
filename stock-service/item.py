import json
import uuid


class Item:
    def __init__(
        self,
        price,
    ):
        self.item_id = str(uuid.uuid4())
        self.price = price
        self.amount = 0

    def toJSON(self):
        return json.dumps(self.__dict__)

    def add_amount(self, amount):
        self.amount += amount
        return True

    def subtract_amount(self, amount):
        try:
            if self.amount - amount < 0:
                return False
            self.amount -= amount
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
