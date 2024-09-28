from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save

from billing.models import BillingProfile
from orders.models import Order

import stripe

User = settings.AUTH_USER_MODEL


class PaypalPayment(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    paypalOrderID = models.CharField(null=True, blank=True, default=None, max_length=128)
    paypalPayerID = models.CharField(null=True, blank=True, default=None, max_length=128)
    brainTreeID = models.CharField(null=True, blank=True, default=None, max_length=128)


class StripeManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        created = False
        obj = False
        return obj, created
    
    def add_new(self, billing_profile, token):
        if token:
            customer = stripe.Customer.retrieve(self.customer_id)
            stripe_card_response = customer.sources.create(source=token)
        if str(stripe_card_response.object) == "card":
            new_card_obj = self.model(
                billing_profile=billing_profile,
                stripe_id=stripe_card_response.id,
                brand=stripe_card_response.brand,
                country=stripe_card_response.country,
                exp_month=stripe_card_response.exp_month,
                exp_year=stripe_card_response.exp_year,
                last4=stripe_card_response.last4
            )
            new_card_obj.save()
            return new_card_obj
        return None
    

class StripePayment(models.Model):
    user = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    billing_profile = models.ForeignKey(BillingProfile, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    stripe_id = models.CharField(null=True, blank=True, default=None, max_length=128)
    amount_charged = models.CharField(null=True, blank=True, default=None, max_length=128)
    currency = models.CharField(null=True, blank=True, default=None, max_length=128)
    last4 = models.CharField(null=True, blank=True, default=None, max_length=128)
    card_type = models.CharField(null=True, blank=True, default=None, max_length=128)
    description = models.CharField(null=True, blank=True, default=None, max_length=128)
    risk_level = models.CharField(null=True, blank=True, default=None, max_length=128)
    risk_score = models.FloatField(null=True, blank=True, default=None)
    seller_message = models.CharField(null=True, blank=True, default=None, max_length=128)
    outcome_type = models.CharField(null=True, blank=True, default=None, max_length=128)
    is_paid = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)
    receipt_url = models.URLField(max_length=256)
    meta_data = models.TextField(null=True, blank=True)

    objects = StripeManager()


class PaymentManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        created = False
        obj = False
        return obj, created


class CardManager(models.Manager):
    def all(self, *args, **kwargs):
        return self.get_queryset().filter(active=True)




class Card(models.Model): # use this in paymwnt.stripe model
    billing_profile = models.ForeignKey(
        BillingProfile, null=True, on_delete=models.SET_NULL)
    stripe_id = models.CharField(max_length=120)
    brand = models.CharField(max_length=120, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)
    last4 = models.CharField(max_length=4, null=True, blank=True)
    default = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    meta_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return "{} {}".format(self.brand, self.last4)


class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None):
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None:
            return False, "No cards available"

        c = stripe.Charge.create(
            amount=int(order_obj.total * 100),
            currency="gbp",
            customer=billing_profile.customer_id,
            source=card_obj.stripe_id,
            metadata={"Order_id: ": order_obj.order_id},
        )
        new_charge_obj = self.model(
            billing_profile=billing_profile,
            stripe_id=c.id,
            paid=c.paid,
            refunded=c.refunded,
            outcome=c.outcome,
            outcome_type=c.outcome['type'],
            seller_message=c.outcome.get('seller_message'),
            risk_level=c.outcome.get('risk_level'),
        )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message


def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(
            billing_profile=billing_profile).exclude(
            pk=instance.pk)
        qs.update(default=False)


post_save.connect(new_card_post_save_receiver, sender=Card)


class Charge(models.Model):
    billing_profile = models.ForeignKey(
        BillingProfile, null=True, on_delete=models.SET_NULL)
    stripe_id = models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(null=True, blank=True)
    outcome_type = models.CharField(max_length=120, null=True, blank=True)
    seller_message = models.CharField(max_length=120, null=True, blank=True)
    risk_level = models.CharField(max_length=120, null=True, blank=True)
    meta_data = models.TextField(null=True, blank=True)

    objects = ChargeManager()


class Payment(models.Model):
    user = models.ForeignKey(
        User,
        default=None,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    stripe = models.ForeignKey(StripePayment, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    paypal = models.ForeignKey(PaypalPayment, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    paymentMethod = models.CharField(null=True, blank=True, default=None, max_length=128)
    is_paid = models.BooleanField(default=False)
    summery = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    meta_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = PaymentManager()

    def __str__(self):
        return "Order: " + self.order.order_id
    
    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)
