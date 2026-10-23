from django.dispatch import Signal
from django.db.models.signals import pre_save

from .models import Product

from decimal import Decimal
from ecommerce.utils import unique_slug_generator

def product_pre_save_reciever(sender, instance, *args, **kwargs):
    instance.vat = instance.price * Decimal(0.2)
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_reciever, sender=Product)