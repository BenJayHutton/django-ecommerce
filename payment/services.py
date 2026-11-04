import json
import logging
import stripe
from django.conf import settings
from django.views.generic import View
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from carts.models import Cart
from products.models import Product

from .models import (
    Stripe,
    StripeCharge,
    StripeCheckoutSession,
    StripePaymentIntent,
    StripeProduct,
    StripePrice,
    StripeCustomer
    )

now = timezone.now()
stripe_debugger = logging.getLogger("stripe_debugger")
stripe_api_key = settings.STRIPE_SECRET_API_KEY
stripe_public_key = settings.STRIPE_PUB_KEY
stripe_webhook_secret = settings.STRIPE_WEBHOOK_SECRET

if stripe_api_key:
    client = stripe.StripeClient(stripe_api_key)
else:
    client = None


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(View):
    
    def post(self, request):
        payload = request.body
        checkout_session_obj = None
        try:
            event = json.loads(payload) or None
        except json.decoder.JSONDecodeError as e:
            stripe_debugger.debug(f'Webhook error while parsing basic request. {type(e)} {e}', exc_info=True)
            data = {"success":False}
            return JsonResponse(data)
        if stripe_webhook_secret:
            # Only verify the event if there is an endpoint secret defined
            # Otherwise use the basic event deserialized with json
            sig_header = request.headers.get('stripe-signature')
            try:
                event = client.construct_event(
                    payload, sig_header, stripe_webhook_secret
                )
            except stripe.error.SignatureVerificationError as e:
                stripe_debugger.debug(f'Webhook signature verification failed. {type(e)}: {e}', exc_info=True)
                data = {"success":False}
                return JsonResponse(data)
        event_type_id = event['data']['object']['id']
        event_type = event['type']
        event_id = event['id']

        match event['type']:
            case "checkout.session.completed":
                try:
                    event_obj = event["data"]["object"]
                    checkout_session_obj, created = StripeCheckoutSession.objects.new_or_get(event=event_obj)
                    cart_obj = Cart.objects.get(id=event_obj["metadata"]["cart_obj"])
                    for cart_item in cart_obj.cart_items.all():
                        product = Product.objects.get(id=cart_item.product.id)
                        old_qty, new_qty = product.decrease_qty_of_product(quantity=cart_item.quantity)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] checkout.session.completed error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)
            case "charge.updated":
                try:
                    stripe_obj, created = StripeCharge.objects.new_or_get(event=event)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] charge.updated error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)
            case "charge.succeeded":
                try:
                    charge_obj, created = StripeCharge.objects.new_or_get(event=event)
                    charge_obj.is_paid = True
                    charge_obj.save()
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] charge.succeeded error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)                    
            case "payment_intent.created":
                try:
                    stripe_obj = StripePaymentIntent.objects.new_or_get(event=event)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] payment_intent.created error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)                    
            case "payment_intent.succeeded":
                try:
                    stripe_obj = StripePaymentIntent.objects.new_or_get(event=event)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] payment_intent.succeeded error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)                    
            case "product.created":
                try:
                    stripe_obj = StripeProduct.objects.new_or_get(event=event)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] product.created error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)                    
            case "price.created":
                try:
                    stripe_obj = StripePrice.objects.new_or_get(event=event)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] price.created error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)                    
            case "customer.created":
                try:
                    stripe_obj = StripeCustomer.objects.new_or_get(event=event)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] customer.created error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)                    
            case "customer.updated":
                try:
                    stripe_obj = StripeCustomer.objects.new_or_get(event=event)
                except Exception as e:
                    stripe_debugger.debug(f'[{now}] customer.updated Error.\n{type(e)} {e}', exc_info=True)
                    data = {"success":False}
                    return JsonResponse(data)                    
            case _:
                stripe_debugger.debug(f'[{now}] Unhandled event type {event_type}: {event_id}\n{event}')
        data = {"success":True}
        return JsonResponse(data)
