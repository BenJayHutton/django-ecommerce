from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, ListView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.utils.http import urlencode
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from billing.models import BillingProfile
from accounts.models import GuestEmail
from orders.models import Order
from carts.models import Cart
from products.models import Product
from .models import Payment

import json
import stripe
import os


class Paypal(View):
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body.decode("utf-8"))
        user = None
        cart_obj = Cart.objects.get(pk=request.session["cart_id"])
        if request.user.is_authenticated:
            user = request.user

        paymentMethod = body["paymentMethod"]
        orderPk = body["orderPk"]
        orderId = body["orderId"]
        total = body["total"]
        vat = body["vat"]
        shipping = body["shipping"]
        subTotal = body["subTotal"]
        paypalOrderID = body["paypalOrderID"]
        paypalPayerID = body["paypalPayerID"]
        is_paid = body["is_paid"]

        order_obj = Order.objects.get(pk=orderPk)
        is_prepared = order_obj.check_done()
        if is_prepared:
            if is_paid:
                order_obj.mark_paid()
                for item in cart_obj.cart_items.all():
                    Product.objects.decrease_qty_of_product(
                        quantity=item.quantity, id=item.product.id)
                request.session['cart_item_count'] = 0
                del request.session['cart_id']
                new_payment_obj = Payment.objects.get_or_create(
                    user=user,
                    order=order_obj,
                    paymentMethod=paymentMethod,
                    paypalOrderID=paypalOrderID,
                    paypalPayerID=paypalPayerID,
                    is_paid=True,
                    summery=body,
                    total=subTotal
                )
                return JsonResponse({"cartSuccess": True})
            else:
                return JsonResponse({"cartSuccess": False})
        return JsonResponse({"cartSuccess": False})


class BrainTree(View):
    def post(self, request, *args, **kwargs):
        pass


class Stripe(View):
    api_key = stripe.api_key = os.environ.get("STRIPE_SECRET_API_KEY", None)

    def post(self, request, *args, **kwargs):
        pass


class StripeWebHook(View):
    stripe.api_key = os.environ.get("STRIPE_SECRET_API_KEY")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(StripeWebHook, self).dispatch(*args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        try:
            event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET")
            )

        except ValueError as e:
            # Invalid payload
            print("invalid payload", e)
            return HttpResponse(status=400)
        
        except stripe.error.SignatureVerificationError as e:
            # invalid signature
            print("invalid webhook signature", e)
            return HttpResponse(status=400)

        # Handle the event
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object # contains a stripe.PaymentIntent
            print('PaymentIntent was successful!')
        elif event.type == 'payment_method.attached':
            payment_method = event.data.object # contains a stripe.PaymentMethod
            print('PaymentMethod was attached to a Customer!')
        # ... handle other event types
        else:
            print('Unhandled event type {}'.format(event.type))

        if event.type == 'checkout.session.completed':
            session = event['data']['object']
            customer_email = session["customer_details"]["email"]
            order_id = session["metadata"]["order_id"]
            order_obj = Order.objects.get(order_id=order_id)
            order_obj.mark_paid()
            Order.objects.email_order(order_id)
            request.session['cart_item_count'] = 0
            del request.session['cart_id']
        return HttpResponse(status=200)


class StripeCharge(ListView):
    stripe.api_key = os.environ.get("STRIPE_SECRET_API_KEY", None)
    template_name = 'payment/home.html'

    def post(self, request, *args, **kwargs):
        line_items = []
        cart_id = self.kwargs["pk"]
        order_id = self.kwargs["order_id"]
        customer_email = self.kwargs["customer_email"]
        if request.user.is_authenticated:
            customer_obj = BillingProfile.objects.get(email=customer_email)
        else:
            customer_obj = GuestEmail.objects.filter(email=customer_email).first()

        cart_obj = Cart.objects.get(id=cart_id)
        order_obj = Order.objects.get(order_id=order_id)
        
        cart_items = cart_obj.cart_items.all()

        for item in cart_items:
            line_item = {
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': item.product.title,
                    },
                    'unit_amount': item.product.price_in_pennies(),
                },
                'quantity': item.quantity,
            }
            line_items.append(line_item)
        
        vat = {
            'price_data':{
            'currency': 'gbp',
            'product_data':{
            'name': 'Vat',
            },
            'unit_amount': int(cart_obj.vat*100),
            },
            'quantity':1,
        }
        line_items.append(vat)
        
        cart_shipping = {
        'price_data': {
        'currency': 'gbp',
        'product_data':{
        'name': 'Shipping',
                },
                'unit_amount': int(cart_obj.shipping*100),
            },
            'quantity': 1,
        }
        line_items.append(cart_shipping)

        YOUR_DOMAIN = os.environ.get("BASE_URL_LOCAL", os.environ.get("BASE_URL"))
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            metadata={
                'order_id': order_obj.order_id,
            },
            customer_email=customer_obj.email,
            mode='payment',
            success_url=YOUR_DOMAIN + reverse('cart:success'),
            cancel_url=YOUR_DOMAIN + reverse('cart:checkout'),
        )
        return redirect(checkout_session.url)
