from order import Order
import uuid
import pytest
import json

def test_order_init():
    order = Order(user_id="1")
    assert order.order_id != None
    assert order.paid == False
    assert order.items == []
    assert order.user_id == "1"
    assert order.total_cost == 0

def test_order_to_json():
    order = Order(user_id="1")
    order_json = order.toJSON()
    assert order_json != None
    assert order_json != ""
    assert order_json == json.dumps(order.__dict__)

def test_order_from_json():
    order = Order(user_id="1")
    order_json = order.toJSON()
    order2 = Order.fromJSON(order_json)
    assert order == order2

def test_order_add_item():
    order = Order(user_id="1")
    assert order.add_item("1") == True
    assert order.items == ["1"]

def test_order_remove_item():
    order = Order(user_id="1", items=["1"])
    assert order.remove_item("1") == True
    assert order.items == []

def test_order_remove_item_not_in_list():
    order = Order(user_id="1")
    assert order.remove_item("1") == True
    assert order.items == []

def test_order_pay():
    order = Order(user_id="1")
    order.pay()
    assert order.paid == True
