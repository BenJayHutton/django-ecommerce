from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from decimal import Decimal

from accounts.models import User
from billing.models import BillingProfile
from bookkeeping.models import CashBook
from orders.models import Order

import stripe
import logging

project_debug_log = logging.getLogger("project_debug_log")
project_access_log = logging.getLogger("project_access_log")

now = timezone.now()

stripe_api_key = settings.STRIPE_SECRET_API_KEY
if stripe_api_key:
    stripe.api_key = stripe_api_key
    client = stripe.StripeClient(stripe_api_key)

PAYMENT_STATUS = (
    ('UNPAID','Unpaid'),
    ('PAID','Paid'),
    ('SUBSCRIPTION','Subscription'),
    ('UNPAID','Unpaid'),
    ('REFUNDED','Refunded'),
    ('DECLINED','Declined'),
    ('CANCELLED','Cancelled'),
    ('CREATED','Created'),
)

PAYMENT_PROCESSOR = (
    ('STRIPE', 'Stripe'),
    ('PAYPAL', 'PayPal'),
    ('CASH', 'Cash'),
    ('NO_PAYMENT', 'No payment'),
)

class PaypalPaymentManager(models.Manager):
    def new_or_get(self, request):
        user_obj = request.user
        billing_profile_obj = BillingProfile.object.new_or_get(request)
        created = False
        
        return created


class PaypalPayment(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    paypalOrderID = models.CharField(null=True, blank=True, default=None, max_length=128)
    paypalPayerID = models.CharField(null=True, blank=True, default=None, max_length=128)
    brainTreeID = models.CharField(null=True, blank=True, default=None, max_length=128)

    objects = PaypalPaymentManager()


class StripeCheckoutSessionManager(models.Manager):
    def new_or_get(self, *args, **kwargs):
        event = kwargs['event']
        project_access_log.debug(f'[{now}] [StripeCheckoutSession new_or_get]\n{event}')
        created = False
        checkout_session_id=event["id"]
        stripe_obj = self.get_queryset().filter(checkout_session_id=checkout_session_id)
        amount_total = Decimal(int(event['amount_total'])/100)
        amount_subtotal = Decimal(int(event['amount_subtotal'])/100)
        customer_email = event['customer_email']
        payment_intent_id = event['payment_intent']

        try:
            if stripe_obj.exists():
                for obj in stripe_obj:
                    obj.payment_intent_id = payment_intent_id
                    obj.payment_status = event["payment_status"]
                    obj.metadata = event
                    obj.save()
            else:
                stripe_obj = self.model.objects.create(
                    checkout_session_id=checkout_session_id,
                    payment_intent_id = payment_intent_id,
                    customer_email = customer_email,
                    total = amount_total,
                    sub_total = amount_subtotal,
                    vat = Decimal(0),
                    currency = event["currency"],
                    payment_status = event["payment_status"],
                    metadata = event
                    )
                created = True
        except Exception as E:
            print(f"StripeCheckoutSession new or get error: {type(E)}: {E}")
            raise
        return stripe_obj, created

    def get_stripe_checkout_session(self, *args, **kwargs):
        session_id = None
        return session_id


class StripeCheckoutSession(models.Model):
    checkout_session_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    payment_intent_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    customer_email = models.EmailField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)
    failure_message = models.CharField(null=True, blank=True, default=None, max_length=128)
    sub_total = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    vat = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    total = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    card_brand = models.CharField(null=True, blank=True, default=None, max_length=128)
    last_4 = models.CharField(null=True, blank=True, default=None, max_length=128)
    currency = models.CharField(default="GBP", max_length=3)
    payment_status = models.CharField(choices=PAYMENT_STATUS, default='CREATED', max_length=128)
    is_paid = models.BooleanField(default=False)
    metadata = models.TextField(default=None, null=True, blank=True)
    outcome_type = models.CharField(null=True, blank=True, default=None, max_length=128)
    receipt_url = models.URLField(null=True, blank=True, default=None, max_length=256)
    risk_level = models.CharField(null=True, blank=True, default=None, max_length=128)
    risk_score = models.FloatField(default=0)
    seller_message = models.CharField(null=True, blank=True, default=None, max_length=128)

    objects = StripeCheckoutSessionManager()

    def __str__(self):
        return str(self.checkout_session_id)


class StripePaymentIntentManager(models.Manager):
    def new_or_get(self, request=None, *args, **kwargs):
        event = kwargs['event']
        created = False
        payment_intent_id=event["data"]["object"]["id"]
        obj =  self.get_queryset().filter(payment_intent_id=payment_intent_id)
        if obj.exists():
            for obj in obj:
                obj.metadata = event
                obj.save()
        else:
            obj = self.model.objects.create(payment_intent_id=payment_intent_id)
            obj.metadata = event
            obj.save()
            created = True
        return obj, created
    
    def get_stripe_payment_intent(self, *args, **kwargs):
        payment_id = None
        return payment_id


class StripePaymentIntent(models.Model):
    payment_intent_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    customer_email = models.EmailField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)    
    metadata = models.TextField(default=None, null=True, blank=True)

    objects = StripePaymentIntentManager()

    def __str__(self):
        return str(self.payment_intent_id)


class StripeChargeManager(models.Manager):
    def new_or_get(self, event, request=None):
        created = False
        charge_id=event["data"]["object"]["id"]
        obj =  self.get_queryset().filter(charge_id=charge_id)
        if obj.exists():
            for obj in obj:
                obj.metadata = event
                obj.save()
        else:
            obj = self.model.objects.create(
                charge_id=charge_id,
                customer_email=event["data"]["object"]["billing_details"]["email"],
                payment_intent_id=event["data"]["object"]["payment_intent"],
                amount=event["data"]["object"]["amount"],
                amount_captured=event["data"]["object"]["amount_captured"],
                balance_transaction=event["data"]["object"]["balance_transaction"],
                metadata=event)
            created = True
        return obj, created

    def get_stripe_charge(self, *args, **kwargs):
        charge_id = None
        return charge_id


class StripeCharge(models.Model):
    charge_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    payment_intent_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    customer_email = models.EmailField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    amount_captured = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    balance_transaction = models.CharField(null=True, blank=True, default=None, max_length=128)
    is_paid = models.BooleanField(default=False)
    metadata = models.TextField(default=None, null=True, blank=True)

    objects = StripeChargeManager()

    def __str__(self):
        return str(self.charge_id)


class StripeProductManager(models.Manager):
    def new_or_get(self, event, request=None):
        created = False
        product_id=event["data"]["object"]["id"]
        obj =  self.get_queryset().filter(product_id=product_id)
        if obj.exists():
            for obj in obj:
                obj.metadata = event
                obj.save()
        else:
            obj = self.model.objects.create(product_id=product_id, metadata=event)
            created = True
        return obj, created

    def get_stripe_product(self, *args, **kwargs):
        product_id = None
        return product_id


class StripeProduct(models.Model):
    product_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)    
    metadata = models.TextField(default=None, null=True, blank=True)

    objects = StripeProductManager()

    def __str__(self):
        return str(self.product_id)


class StripePriceManager(models.Manager):
    def new_or_get(self, event, request=None):
        created = False
        price_id=event["data"]["object"]["id"]
        obj =  self.get_queryset().filter(price_id=price_id)
        if obj.exists():
            for obj in obj:
                obj.metadata = event
                obj.save()
        else:
            obj = self.model.objects.create(price_id=price_id, metadata=event)
            created = True
        return obj, created

    def get_stripe_price(self, *args, **kwargs):
        price_id = None
        return price_id


class StripePrice(models.Model):
    price_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)
    metadata = models.TextField(default=None, null=True, blank=True)

    objects = StripePriceManager()

    def __str__(self):
        return str(self.price_id)


class StripeCustomerManager(models.Manager):
    def new_or_get(self, event, request=None):
        created = False
        customer_id=event["data"]["object"]["id"]
        delinquent = event["data"]["object"]["delinquent"]
        obj =  self.get_queryset().filter(customer_id=customer_id)
        if obj.exists():
            for obj in obj:
                obj.balance = event["data"]["object"]["balance"]
                obj.delinquent = event["data"]["object"]["delinquent"]
                obj.metadata = event
                obj.save()
        else:
            obj = self.model.objects.create(customer_id=customer_id, metadata=event, delinquent=delinquent)
            created = True
        return obj, created

    def find_or_create_stripe_customer_api(self,email=None, customer_id=None, *args, **kwargs):
        email = email
        customer_id = customer_id
        customer_obj = None
        
        if customer_id is not None:
            try:
                customer_obj = client.v1.customers.retrieve("{{customer_id}}")
                project_access_log(f'[{now}] find_or_create_stripe_customer_api Customer_obj\n{customer_obj}')
            except Exception as e:
                project_debug_log.debug(f'[{now}] find_or_create_stripe_customer_api error: {type(e)}: {e}')
        elif email is not None:
            try:
                customer_obj = client.v1.customers.search({"query": f'email:\"{email}\"'})
                project_access_log.debug(f'[{now}] find_or_create_stripe_customer_api Customer_obj\n{customer_obj}')
            except Exception as e:
                project_debug_log.debug(f'[{now}] find_or_create_stripe_customer_api error: {type(e)}: {e}')
        return customer_obj        


class StripeCustomer(models.Model):
    customer_id = models.CharField(unique=True, null=True, blank=True, default=None, max_length=128)
    email = models.EmailField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)
    full_name = models.CharField(null=True, blank=True, default=None, max_length=128)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    delinquent = models.BooleanField(default=False)
    metadata = models.TextField(default=None, null=True, blank=True)

    objects = StripeCustomerManager()

    def __str__(self):
        return str(self.customer_id)


class StripeManager(models.Manager):
    def new_or_get(self, user_obj=None, order_obj=None, checkout_session_obj=None, payment_intent_obj=None, charge_obj=None, customer_obj=None):
        created = False
        stripe_obj = None

        if checkout_session_obj is not None:
            qs = self.get_queryset().filter(checkout_session__in=checkout_session_obj)
        elif payment_intent_obj is not None:
            qs = self.get_queryset().filter(payment_intent__in=payment_intent_obj)
        elif charge_obj is not None:
            qs = self.get_queryset().filter(charge_obj__in=charge_obj)
        elif order_obj is not None:
            qs = self.get_queryset().filter(order_obj__in=order_obj)
        elif customer_obj is not None:
            qs = self.get_queryset().filter(customer_obj__in=customer_obj)

        if qs.exists():
            for qs in qs:
                if order_obj is not None:
                    qs.order = order_obj
                    qs.save()
                if user_obj is not None and qs.user is not None:
                    for user in user_obj:
                        qs.user = user
                        qs.save()
        else:
            stripe_obj = self.model.objects.create()
            if checkout_session_obj is not None:
                for obj in checkout_session_obj:
                    stripe_obj.checkout_session = obj
                    stripe_obj.save()
            elif user_obj is not None :
                for user in user_obj:
                    stripe_obj.user = user
                    stripe_obj.save()
            elif order_obj is not None:
                for order in order_obj:
                    stripe_obj.order = order
                    stripe_obj.save()
            elif payment_intent_obj is not None:
                for payment in payment_intent_obj:
                    stripe_obj.payment_intent = payment
                    stripe_obj.save()
            created = True
        return stripe_obj, created
        

class Stripe(models.Model):
    user = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    checkout_session = models.ForeignKey(StripeCheckoutSession, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    payment_intent = models.ForeignKey(StripePaymentIntent, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    charge = models.ForeignKey(StripeCharge, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(StripeCustomer, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)    
    metadata = models.TextField(default=None, null=True, blank=True)

    objects = StripeManager()

    class Meta:
        verbose_name_plural = "Stripe"

    def __str__(self):
        return str(f"Stripe entry: {self.user} - {self.order} - {self.checkout_session}")
