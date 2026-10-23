from django.db.models.signals import pre_save, post_save

from ecommerce.utils import unique_order_id_generator

from .models import Order

def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(
        cart=instance.cart).exclude(
        billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_order_shipped(sender, instance, created, *args, **kwargs):
    if instance.status=="shipped":
        order_obj = Order
        order_obj.objects.email_order_shipped(order_id=instance.order_id)

post_save.connect(post_save_order_shipped, sender=Order)
