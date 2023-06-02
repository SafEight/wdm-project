import json
import uuid


class Order:
    def __init__(self, user_id, order_id=str(uuid.uuid4()), paid=False, items=[], total_cost=0):
        self.order_id = order_id
        self.paid = paid
        self.items = items
        self.user_id = user_id
        self.total_cost = total_cost

    def toJSON(self):
        return json.dumps(self.__dict__)

    def add_item(self, item_id):
        self.items.append(item_id)
        return True

    def remove_item(self, item_id):
        try:
            self.items.remove(item_id)
            return True
        except ValueError as ve:
            return False

    def pay(self):
        self.paid = True

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Order):
            return self.order_id == __o.order_id

    @staticmethod
    def fromJSON(json_string):
        json_dict = json.loads(json_string)
        order = Order(**json_dict)
        return order
    
