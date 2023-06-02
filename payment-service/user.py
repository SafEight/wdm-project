import json
import uuid


class User:
    def __init__(
        self,
    ):
        self.user_id = str(uuid.uuid4())
        self.funds = 0

    def toJSON(self):
        return json.dumps(self.__dict__)

    def add_funds(self, amount):
        self.funds += amount
        return True

    def pay(self, amount):
        try:
            if self.funds - amount < 0:
                return False
            self.funds -= amount
            return True
        except ValueError as ve:
            return False

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, User):
            return self.user_id == __o.user_id

    @staticmethod
    def fromJSON(json_string):
        json_dict = json.loads(json_string)
        user = User(**json_dict)
        return user
