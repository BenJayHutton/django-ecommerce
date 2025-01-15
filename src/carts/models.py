from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, m2m_changed
from products.models import Product
from django.urls import reverse

from shipping.views import RoyalMail

User = settings.AUTH_USER_MODEL


class CartItemManagerQuerySet(models.query.QuerySet):
    def update_total(self):
        return self.aggregate(Sum("total"))

    def update_total_weight(self):
        return self.aggregate(Sum("weight_in_grams"))
   

class CartItemManager(models.Manager):
    def get_queryset(self):
        return CartItemManagerQuerySet(self.model, using=self._db)
    
    def new_or_get(self, request, *args, **kwargs):
        if not request.session.exists(request.session.session_key):
            request.session.create()
        cart_item_id = request.session.get("cart_item_id", None)
        session_id = request.session.session_key
        product_obj = kwargs.get("product_obj", None)
        product_quantity = kwargs.get("product_quantity", None)
        qs = self.get_queryset().filter(id=cart_item_id, product=product_obj)
        if qs:
            cart_item_obj = qs.first()
            new_item_obj = False
            if product_obj and cart_item_obj.product is None:
                cart_item_obj.product = product_obj
                cart_item_obj.save()
            if product_quantity:
                cart_item_obj.quantity = product_quantity
                cart_item_obj.save()
        else:
            cart_item_obj = CartItem.objects.create(
                session_id=session_id, quantity=product_quantity, product=product_obj)
            if product_obj and cart_item_obj.product is None:
                cart_item_obj.product = product_obj
                cart_item_obj.save()
            new_item_obj = True
            request.session['cart_item_id'] = cart_item_obj.id
        return cart_item_obj, new_item_obj
    
    def total_weight_in_grams(self, request, *args, **kwargs):
        cart_item_obj = kwargs.get("cart_item_obj", None)
        cart_item_weight_in_grams = kwargs.get("cart_item_weight_in_grams", 0)
        product_quantity = kwargs.get("product_quantity", 0)
        total = float(cart_item_weight_in_grams * product_quantity)
        cart_item_obj.weight_in_grams = total
        return total 

class CartItem(models.Model):
    product = models.ForeignKey(
        Product,
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=None, null=True)
    price_of_item = models.FloatField(default=0.00, max_length=2)
    session_id = models.CharField(
        max_length=120,
        default=0,
        null=True,
        blank=True)
    total = models.FloatField(default=0.00, max_length=2)
    weight_in_grams = models.FloatField(null=True, blank=True, default=0.00, max_length=2)
    meta_data = models.TextField(null=True, blank=True)

    objects = CartItemManager()

    def __str__(self):
        to_return = "Cart basket: " + str(self.id) + " - " + self.product.title
        return to_return


class CartManager(models.Manager):

    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            cart_obj = qs.first()
            new_obj = False
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)

    def calculate_cart_total(self, *args, **kwargs):
        cart_obj = kwargs.get("cart_obj", None)
        total = 0
        vat = 0
        sub_total = 0
        shipping_cost = cart_obj.shipping
        for x in cart_obj.cart_items.all():
            total += x.total
        vat = round(total * 0.2, 2)
        if vat < 0.01:
            vat = 0
        sub_total = round(total + vat + shipping_cost, 2)
        return total, vat, sub_total

    def total_weight_in_grams(self, request, *args, **kwargs):
        cart_obj = kwargs.get("cart_obj", None)
        weight_in_grams = float(0.00)
        for x in cart_obj.cart_items.all():
            weight_in_grams += x.weight_in_grams
        return weight_in_grams

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    cart_items = models.ManyToManyField(CartItem, default=None, blank=True)
    total = models.FloatField(default=0.00, max_length=2)
    vat = models.FloatField(default=0.00, max_length=2)
    shipping = models.FloatField(default=0.00, max_length=2)
    subtotal = models.FloatField(default=0.00, max_length=2)
    weight_in_grams = models.FloatField(null=True, blank=True, default=0.00, max_length=2)
    meta_data = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    @property
    def is_digital(self):
        qs = self.cart_items.all()
        for x in qs:
            if not x.product.is_digital:
                return False
        return True

    def get_absolute_url(self):
        return reverse("cart:detail", kwargs={'pk': self.pk})


def cart_item_pre_save_reciever(sender, instance, *args, **kwargs):
    try:
        quantity = int(instance.quantity)
    except BaseException:
        quantity = 0
    try:
        price_of_item = instance.product.price
    except BaseException:
        price_of_item = 0

    instance.price_of_item = price_of_item
    instance.total = quantity * price_of_item


pre_save.connect(cart_item_pre_save_reciever, sender=CartItem)


def cart_post_save_reciever(sender, instance, *args, **kwargs):
    cart_items = instance.cart_items.all()
    royal_mail_obj = RoyalMail
    vat = float(0.00)
    sub_total = float(0.00)
    cart_item_total = cart_items.update_total()['total__sum']
    total_weight_in_grams = cart_items.update_total_weight()['weight_in_grams__sum']
    shipping_cost = royal_mail_obj.get_shipping_cost(
        royal_mail_obj, total_weight_in_grams)
    if cart_item_total is None:
        cart_item_total = float(0.00)
    vat = round(cart_item_total * 0.2, 2)
    if vat < 0.01:
        vat = 0
    sub_total = round(cart_item_total + vat + shipping_cost, 2)
    instance.weight_in_grams = total_weight_in_grams
    instance.total = cart_item_total
    instance.vat = vat
    instance.shipping = shipping_cost
    instance.subtotal = sub_total


post_save.connect(cart_post_save_reciever, sender=Cart)


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        royal_mail_obj = RoyalMail
        vat = float(0.00)
        sub_total = float(0.00)
        cart_items = instance.cart_items.all()
        cart_item_total = cart_items.update_total()['total__sum']
        total_weight_in_grams = cart_items.update_total_weight()['weight_in_grams__sum']
        shipping_cost = royal_mail_obj.get_shipping_cost(
        royal_mail_obj, total_weight_in_grams)
        if cart_item_total is None:
            cart_item_total = 0
        vat = round(cart_item_total * 0.2, 2)
        if vat < 0.01:
            vat = 0
        sub_total = cart_item_total + vat + shipping_cost
        instance.weight_in_grams = total_weight_in_grams
        instance.vat = vat
        instance.shipping = shipping_cost
        instance.subtotal = sub_total
        instance.save()


m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.cart_items.through)
