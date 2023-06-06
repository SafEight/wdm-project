from antidotedb import AntidoteClient, Key, Counter
from random import randint
import uuid

def id(): randint(0, 99999999)

db = AntidoteClient('192.168.49.2', 31167)
user_id = str(uuid.uuid4())
key = Key("payment", user_id, "COUNTER")
tx = db.start_transaction()
tx.update_objects(Counter.IncOp(key, 0))
print(tx.read_objects(key))                      O
print(tx.read_objects(key)[0])
print(tx.read_objects(key)[0].value())
tx.commit()