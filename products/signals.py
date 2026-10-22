from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from products.models import Product

from eCommerce.utils import unique_slug_generator

@receiver(pre_save, sender=Product)
def product_pre_save_reciever(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)