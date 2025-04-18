from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from eCommerce.utils import unique_order_id_generator
from .models import Order
from carts.models import Cart


@receiver(pre_save, sender=Order)
def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(
        cart=instance.cart).exclude(
        billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)


@receiver(post_save, sender=Cart)
def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        weight_in_grams = cart_obj.weight_in_grams
        qs = Order.objects.filter(cart__id=cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total(weight_in_grams=weight_in_grams)


@receiver(post_save, sender=Order)
def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()


@receiver(post_save, sender=Order)
def post_save_order_shipped(sender, instance, created, *args, **kwargs):
    if instance.status=="shipped":
        order_obj = Order
        order_obj.objects.email_order_shipped(order_id=instance.order_id)
