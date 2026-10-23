from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from carts.models import Cart


class CartManagerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def make_request(self):
        request = self.factory.get('/')
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()
        return request

    def test_new_or_get_returns_cart_instance(self):
        request = self.make_request()

        cart_obj, created = Cart.objects.new_or_get(request)

        self.assertTrue(created)
        self.assertIsInstance(cart_obj, Cart)
        self.assertEqual(cart_obj.session_key, request.session.session_key)
