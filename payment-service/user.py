import json
import uuid


class User:
    def __init__(
        self,
        user_id,
        credit,
    ):
        self.user_id = user_id
        self.credit = int(credit)

    def toJSON(self):
        return json.dumps(self.__dict__)

    def add_funds(self, amount):
        self.credit += int(amount)
        return True

    def pay(self, amount):
        try:
            if self.credit - int(amount) < 0:
                return False
            self.credit -= int(amount)
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
