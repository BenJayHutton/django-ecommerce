from django.conf import settings
from django.db import models

from decimal import Decimal

from accounts.models import User
from carts.models import Cart

User = settings.AUTH_USER_MODEL

CURRIER_LIST = [
    ("Royal Mail 1st Class", "Royal Mail 1st Class"),
    ("Royal Mail 2nd Class", "Royal Mail 2nd Class"),
    ("International", "International")
]


class CurrierManager(models.Manager):
     
     def new_or_get(self, request, cart=None, currier="Royal Mail 2nd Class"):
        created = False
        user = request.user
        session_key = request.session.session_key
        qs = self.get_queryset().filter(user=user, cart=cart)
        if qs.exists():
            currier_obj = qs.first()
        else:
            if user.is_authenticated:
                currier_obj = self.model.objects.create(user=user, cart=cart, currier=currier, session_key=session_key)
            else:
                currier_obj = self.model.objects.create(cart=cart, currier=currier, session_key=session_key)
            created = True
        return currier_obj, created


class Currier(models.Model):
    user = models.ForeignKey(User, default=None, null=True, on_delete=models.SET_NULL)
    cart = models.ForeignKey(Cart, default=None, null=True, on_delete=models.SET_NULL)
    order = models.CharField(max_length=120, unique=True, blank=True, null=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    currier = models.CharField(max_length=50, default="-", choices=CURRIER_LIST)
    price = models.DecimalField(default=0.00, max_digits=12, decimal_places=4)
    tracking_code = models.CharField(max_length=120, default=" ", null=True, blank=True)
    weight = models.FloatField(default=0.00, max_length=2)
    meta_data = models.TextField(default="", null=True, blank=True)

    class Meta:
        ordering = ["-user"]
        verbose_name = "currier"
        verbose_name_plural = "curriers"
    
    def __str__(self):
        currier = "no currier"
        full_name = ""
        if self.currier is not None:
            currier = self.currier
        if self.user.full_name is not None:
            full_name = self.user.full_name
        return full_name + ", Currier: " + currier
    
    def get_price(*args, **kwargs):
        weight = kwargs.get("weight")
        royal_mail_2nd = RoyalMail.second_class(weight=weight)
        return royal_mail_2nd
    
    objects = CurrierManager()


class RoyalMail():
    def get_shipping_cost(weight=None):
        return  Decimal(RoyalMail.second_class(weight=weight))

    def first_class(weight=None):
        cost=float(0.00)
        if weight is not None:
            if weight ==00:
                cost= 0.00
            elif weight >0 and weight <=100:
                cost = 1.80
            elif weight >= 100 and weight <= 249:
                cost = 2.20
            elif weight >= 250 and weight <= 499:
                cost = 2.50
            elif weight >= 500 and weight <= 749:
                cost = 2.75
            elif weight >= 750 and weight <=1999:
                cost = 5.25
            elif weight > 2000 and weight <=4999:
                cost = 11.95
        return Decimal(cost)

    def second_class(weight=None):
        cost=Decimal(0)
        if weight is not None:
            if weight == 0:
                cost = 0.0
            if weight >0 and weight <=100:
                cost = 1.0
            elif weight >= 100 and weight <= 249:
                cost = 2.0
            elif weight >= 250 and weight <= 499:
                cost = 3.0
            elif weight >= 500 and weight <= 749:
                cost = 4.0
            elif weight >= 750 and weight <=1999:
                cost = 5.0
            elif weight > 2000 and weight <=4999:
                cost = 6.0
            elif weight >= 5000 and weight <=9999:
                cost = 7.0
            elif weight >= 10000 and weight <=14999:
                cost = 8.0
            elif weight >= 15000:
                cost = 9.0
        return Decimal(cost)
