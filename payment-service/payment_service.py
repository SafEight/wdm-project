from user import User
import redis
import os
import uuid

DB = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
    db=int(os.environ["REDIS_DB"]),
)


class PaymentServiceFunctions:
    functions = {}

    @classmethod
    def register(cls, name):
        def inner(func):
            cls.functions[name] = func
            return func

        return inner


class PaymentService:
    def __init__(self):
        self.db: redis.Redis = DB

    def close_db_connection(self):
        self.db.close()

    @PaymentServiceFunctions.register("create_user")
    def create_user(self, user_id=None):
        user = User()
        print(user.toJSON())
        self.db.set(user.user_id, user.toJSON())
        return True, user.user_id

    @PaymentServiceFunctions.register("find_user")
    def find_user(self, user_id=None):
        user_json = self.db.get(user_id)
        if not user_json:
            return False, "User does not exist!"
        return True, user_json

    @PaymentServiceFunctions.register("add_funds")
    def add_funds(self, user_id=None, amount=None):
        user_json = self.db.get(user_id)
        if not user_json:
            return False, "User does not exist!"
        u = User.fromJSON(user_json)
        u.add_funds(amount)
        self.db.set(u.user_id, u.toJSON())
        return True, f"Added funds!: {amount}"

    @PaymentServiceFunctions.register("pay")
    def pay(self, user_id=None, amount=None):
        user_json = self.db.get(user_id)
        if not user_json:
            return False, "User does not exist!"
        u = User.fromJSON(user_json)
        if not u.pay(amount):
            return False, "Insufficient funds!"
        self.db.set(u.user_id, u.toJSON())
        return True, f"Paid!: {amount}"

    @PaymentServiceFunctions.register("cancel")
    def cancel(self, order_id=None):
        return True

    @PaymentServiceFunctions.register("status")
    def status(self, user_id=None, order_id=None):
        return True
