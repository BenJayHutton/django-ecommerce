import json
import stripe
import os
import logging
from flask import jsonify
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone

from billing.models import BillingProfile
from carts.models import Cart
from orders.models import Order
from .models import (
    StripeCheckoutSession,
    StripeCustomer
    )
now = timezone.now()

stripe_api_key = settings.STRIPE_SECRET_API_KEY
if stripe_api_key:
    client = stripe.StripeClient(stripe_api_key)

stripe_logger = logging.getLogger("stripe_logger")
project_debug_log = logging.getLogger("project_debug_log")

class StripeCharge(View):

    def post(self, request):
        email = None
        cart_obj, cart_created = Cart.objects.new_or_get(request)
        user_obj = request.user
        if  not cart_obj or cart_created:
            return jsonify({"error": "Your cart is empty."}, status=400)

        if user_obj.is_authenticated:
            email = user_obj.email
            stripe_customer = StripeCustomer.objects.find_or_create_stripe_customer_api(email=email)
        else:
            email = request.session.get('customer_email')

        if email is not None:
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request, email=email)
        
        if billing_profile is not None:
            order_obj, order_created = Order.objects.new_or_get(billing_profile, cart_obj, session_key=request.session.session_key)
            order_obj.total = cart_obj.total
            order_obj.vat = cart_obj.vat
            order_obj.shipping_total = cart_obj.shipping
            order_obj.subtotal = cart_obj.subtotal
            order_obj.save()
        else:
            return JsonResponse({"error": "Billing profile is required."})
        line_items = []
        product_list = []
        for item in order_obj.cart.cart_items.all():
            product_list.append({
                "product_id": item.id,
                "product_qty": item.quantity
            })
            unit_amount = int(item.product.price * 100)
            line_items.append({
                "price_data": {
                    "currency": "GBP",
                    "unit_amount": unit_amount,
                    "product_data": {
                        "name": item.product.title,
                        "description": item.product.description,
                    },
                },
                "quantity": int(item.quantity),
            })
        shipping_options = [{
            "shipping_rate_data": {
                "type": 'fixed_amount',
                "fixed_amount": {
                    "amount": int(cart_obj.shipping * 100),
                    "currency": 'GBP',
                },
                "display_name": 'Post Office 2nd Class',
                "delivery_estimate": {
                    "minimum": { "unit": "day", "value": 2},
                    "maximum": { "unit": "day", "value": 4},
                },
            },
        },]
        domain = os.environ.get("BASE_URL")
        port = os.environ.get("PORT_LOCAL")
        checkout_path = reverse('cart:checkout')
        checkout_path_success = reverse('cart:success')
        success_url = f"{request.scheme}://{domain}:{port}{checkout_path_success}"
        cancel_url = f"{request.scheme}://{domain}:{port}{checkout_path}"
        session = client.v1.checkout.sessions.create({
            "customer_email":email,
            "line_items":line_items,
            "shipping_options":shipping_options,
            "metadata":{
                "order_id":order_obj.order_id,
                "cart_obj":cart_obj.id
                },
            "mode":"payment",
            "success_url":success_url,
            "cancel_url":cancel_url
        })
        event_name = session['object']
        event_id = session['id']
        stripe_logger.info(f'[{now}] [{event_name}: {event_id}]\n{session}')
        stripe_obj, created = StripeCheckoutSession.objects.new_or_get(request, event=session)
        return JsonResponse({"url": session.url})


class StripeAdminView(View):
    template_name = 'payment/home.html'

    def post(self, request, *args, **kwargs):
        search_obj = request.POST.get("stripe-search")
        result_obj = None #stripe.Customer.search(query=f"email:'{search_obj}' OR name:'{search_obj}'")
        result_json = json.dumps(result_obj, default=str)
        context = {
            'result_obj': result_json
        }
        return render(request, "payment/stripe_admin.html", context)


    def get (self, *args, **kwargs):
        request =  self.request
        client_list = stripe.Customer.list(limit=10)
        charge_list = stripe.Charge.list(limit=10)

        context = {
            'stripe_customer_list': client_list,
            'stripe_charge_list': charge_list,
        }
        return render(request, "payment/stripe_admin.html", context)


class PaypalAdminView(View):
    template_name = 'payment/home.html'

    def get (self, *args, **kwargs):
        request =  self.request
        context = {}
        return render(request, "payment/paypal_admin.html", context)


def payment_success(request):

    session_id = request.GET.get("session_id")

    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
    return render(request, "payment_success.html")
