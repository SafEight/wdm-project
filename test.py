from antidotedb import AntidoteClient, Key, Counter, Map, Flag, Register
import uuid

db = AntidoteClient('192.168.49.2', 31167)
user_id = str(uuid.uuid4())
key = Key("test", user_id, "GMAP")
sub1 = Key("test", "1", "FLAG_EW")
sub2 = Key("test", "2", "FLAG_EW")
k1 = bytes("k1",'utf-8')
k2 = bytes("k2",'utf-8')
val1 = bytes("lightkone",'utf-8')
val2 = bytes("syncfree",'utf-8')
val3 = bytes("concordant",'utf-8')

tx = db.start_transaction()

tx.update_objects(Map.UpdateOp(key, [
    Counter.IncOp( k1, 1, "COUNTER"),
    Flag.UpdateOp(sub1, True),
    Flag.UpdateOp(sub2, False)]))

print(tx.read_objects(key))

tx.commit()
