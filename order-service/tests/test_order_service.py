import pytest
import sys
from order_service import OrderService


def test_create_order():
    os = OrderService()
    result = os.create_order(1)
    assert result[0] == True
    assert result[1] == 1
