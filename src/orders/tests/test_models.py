from django.test import TestCase
from orders.models import Order

class TestOrder(TestCase):
    def setUp(self):
        Order.objects.create(billing_profile = None,order_id = None,shipping_address = None,billing_address = None,cart = None,status ='created', shipping_total = 1,tax = 1,total = 1,active = True)
    
    def test_orders_create_order(self):
        first_user = Order.objects.get(pk=1)
        self.assertEqual(first_user.status, 'created')