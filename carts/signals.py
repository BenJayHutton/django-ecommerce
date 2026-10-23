from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Cart


def cart_item_post_save_reciever(sender, instance, *args, **kwargs):
    try:
        quantity = int(instance.quantity)
        weight_in_grams = instance.product.weight_in_grams
    except BaseException:
        quantity = 0
        weight_in_grams = 0
    try:
        price_of_item = instance.product.price
    except BaseException as e:
        price_of_item = Decimal(0)
    instance.weight_in_grams = quantity * weight_in_grams
    instance.total = quantity * price_of_item


@receiver(post_save, sender=Cart.cart_items.through)
def m2m_changed_cart_receiver(sender, instance, action, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        cart_items = instance.cart_items.all()
        for cart in cart_items:
            total_weight_in_grams += cart.weight_in_grams
        cart_item_total = cart_items.calculate_cart_item_subtotal()['subtotal__sum']
        total_weight_in_grams = cart_items.update_total_weight()['weight_in_grams__sum']
        if cart_item_total is None:
            cart_item_total = 0
        vat = cart_item_total * Decimal(0.2)
        if vat < 0.01:
            vat = 0
        total = cart_item_total + vat + instance.shipping
        instance.weight_in_grams = total_weight_in_grams
        instance.vat = vat
        instance.total = total
        instance.save()
