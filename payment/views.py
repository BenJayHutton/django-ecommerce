import json
import stripe
import os
import logging
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from flask import jsonify
from django.shortcuts import render
from django.views.generic import View
from django.urls import reverse
from django.utils import timezone

from billing.models import BillingProfile
from carts.models import Cart
from orders.models import Order

from .models import (StripeCheckoutSession, StripeCustomer)

now = timezone.now()
project_error_log = logging.getLogger("project_error_log")
stripe_logger = logging.getLogger("stripe_logger")
stripe_error = logging.getLogger("stripe_logger")
stripe_api_key = settings.STRIPE_SECRET_API_KEY

if stripe_api_key:
    client = stripe.StripeClient(stripe_api_key)


class StripeCharge(View):

    def post(self, request):
        try:
            email = None
            cart_obj, cart_created = Cart.objects.new_or_get(request)
            user_obj = request.user
            if hasattr(user_obj, "full_name"):
                full_name = user_obj.full_name
            else:
                full_name = "Guest"
            
            if  not cart_obj or cart_created:
                return jsonify({"error": "Your cart is empty."}, status=400)

            if user_obj.is_authenticated:
                email = user_obj.email
                stripe_customer = StripeCustomer.objects.find_or_create_stripe_customer_api(email=email)
            else:
                email = request.session.get('customer_email')

            if email is not None:
                billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request, email=email)
            
            if billing_profile is not None: # Does the following statement belong here? 
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
                        "product_data": {
                            "name": item.product.title,
                            "description": item.product.description,
                        },                    
                        "unit_amount": unit_amount,
                        "tax_behavior": "exclusive",
                    },
                    "quantity": int(item.quantity),
                })
            shipping_rate = client.v1.shipping_rates.create({
                "display_name": 'tandard delivery',
                "type": "fixed_amount",
                "fixed_amount": {
                    "amount": int(cart_obj.shipping * 100),
                    "currency": "gbp",
                },
                "tax_behavior": "exclusive",
            })

            domain = getattr(settings, 'BASE_URL', None)
            port = getattr(settings, 'PORT', None)
            checkout_path = reverse('cart:checkout')
            checkout_path_success = reverse('cart:success')
            success_url = f"{request.scheme}://{domain}:{port}{checkout_path_success}"
            cancel_url = f"{request.scheme}://{domain}:{port}{checkout_path}"
            address_obj = order_obj.shipping_address
            
            customer = client.v1.customers.create({
                "email": email,
                "name": full_name,
                "address": {
                    "line1": address_obj.address_line_1,
                    "line2": address_obj.address_line_2 or "",
                    "city": address_obj.city,
                    "postal_code": address_obj.postal_code,
                    "country": "GB",
                },
                "shipping": {
                    "name": full_name,
                        "address": {
                        "line1": address_obj.address_line_1,
                        "line2": address_obj.address_line_2 or "",
                        "city": address_obj.city,
                        "postal_code": address_obj.postal_code,
                        "country": "GB",
                    },
                },
            })

            session = client.v1.checkout.sessions.create({
                "customer": customer.id,
                "customer_update": {
                    "shipping": "auto",
                },
                "line_items":line_items,
                "shipping_options":[{
                    "shipping_rate": shipping_rate.id,
                }],
                "shipping_address_collection": {
                    "allowed_countries": ["GB"],
                },
                "metadata":{
                    "order_id":str(order_obj.order_id),
                    "cart_obj":str(cart_obj.id)
                    },
                "mode":"payment",
                "automatic_tax":{"enabled": True},
                "adaptive_pricing": {
                    "enabled": True,
                },
                "success_url":success_url,
                "cancel_url":cancel_url
            })
            event_name = session['object']
            event_id = session['id']
            
            stripe_obj, created = StripeCheckoutSession.objects.new_or_get(request, event=session)
            return JsonResponse({"url": session.url})
        except AttributeError as e:
            project_error_log.log(
                logging.DEBUG if settings.DEBUG else logging.WARNING,
                f'[{now}] StripeCharge AttributeError POST\n{type(e)} {e}', exc_info=True)
            raise AttributeError
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] StripeCharge POST\n{type(e)} {e}', exc_info=True)
            stripe_error.log(
                logging.DEBUG if settings.DEBUG else logging.WARNING,
                f'[{now}] [{event_name}: {event_id}]\n{type(e)} {e}\n{session}', exc_info=True)
            raise Exception


class StripeAdminView(View):
    template_name = 'payment/home.html'

    def post(self, request, *args, **kwargs):
        try:
            search_obj = request.POST.get("stripe-search")
            result_obj = None #stripe.Customer.search(query=f"email:'{search_obj}' OR name:'{search_obj}'")
            result_json = json.dumps(result_obj, default=str)
            context = {
                'result_obj': result_json
            }
            return render(request, "payment/stripe_admin.html", context)
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            raise Exception

    def get (self, *args, **kwargs):
        try:
            request =  self.request
            client_list = stripe.Customer.list(limit=10)
            charge_list = stripe.Charge.list(limit=10)

            context = {
                'stripe_customer_list': client_list,
                'stripe_charge_list': charge_list,
            }
            return render(request, "payment/stripe_admin.html", context)
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] StripeAdminView POST\n{type(e)} {e}', exc_info=True)
            raise Exception


class PaypalAdminView(View):
    template_name = 'payment/home.html'

    def get (self, *args, **kwargs):
        try:
            request =  self.request
            context = {}
            return render(request, "payment/paypal_admin.html", context)
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] PaypalAdminView GET\n{type(e)} {e}', exc_info=True)
            raise Exception


def payment_success(request):
    try:
        session_id = request.GET.get("session_id")
        if session_id:
            session = stripe.checkout.Session.retrieve(session_id)
        return render(request, "payment_success.html")
    except Exception as e:
        project_error_log.log(
        logging.DEBUG if settings.DEBUG else logging.WARNING,
        f'[{now}] def payment_success\n{type(e)} {e}', exc_info=True)
        raise Exception
