from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver
from decimal import Decimal
from carts.models import Cart, CartItem

from shipping.views import RoyalMail

@receiver(pre_save, sender=CartItem)
def cart_item_pre_save_reciever(sender, instance, *args, **kwargs):
    try:
        quantity = int(instance.quantity)
    except BaseException:
        quantity = 0
    try:
        price_of_item = instance.product.price
        print("price_of_item", price_of_item)
    except BaseException:
        price_of_item = Decimal(0.00)

    instance.total = quantity * price_of_item


@receiver(post_save, sender=Cart)
def cart_post_save_reciever(sender, instance, *args, **kwargs):
    royal_mail_obj = RoyalMail
    cart_items = instance.cart_items.all()
    cart_item_total = cart_items.update_total()['total__sum']
    if cart_item_total is None:
        cart_item_total = Decimal(0.00)
    vat = cart_items.update_vat()['vat__sum']
    print("cart_post_save_reciever - vat:", vat)
    if vat is None:
        vat = Decimal(0.00)
        total_weight_in_grams = 0.0
    elif vat < 0.01:
        vat = Decimal(0.00)
    total_weight_in_grams = cart_items.update_total_weight()['weight_in_grams__sum']
    shipping_cost = Decimal(royal_mail_obj.get_shipping_cost(
        royal_mail_obj, total_weight_in_grams))    
    sub_total = cart_item_total + vat + shipping_cost    
    instance.weight_in_grams = total_weight_in_grams
    instance.total = cart_item_total
    instance.vat = vat
    instance.shipping = shipping_cost
    instance.subtotal = sub_total


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        royal_mail_obj = RoyalMail
        vat = Decimal(0.00)
        sub_total = Decimal(0.00)
        cart_items = instance.cart_items.all()
        cart_item_total = cart_items.update_total()['total__sum']
        total_weight_in_grams = cart_items.update_total_weight()['weight_in_grams__sum']
        shipping_cost = Decimal(royal_mail_obj.get_shipping_cost(
        royal_mail_obj, total_weight_in_grams))
        if cart_item_total is None:
            cart_item_total = 0
        vat = cart_item_total * Decimal(0.2)
        if vat < 0.01:
            vat = 0
        sub_total = cart_item_total + vat + shipping_cost
        instance.weight_in_grams = total_weight_in_grams
        instance.vat = vat
        instance.shipping = shipping_cost
        instance.subtotal = sub_total
        instance.save()

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.cart_items.through)