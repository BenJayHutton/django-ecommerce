from django.conf import settings
from django.db import models
from django.db.models import Sum
from products.models import Product
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from shipping.views import RoyalMail

User = settings.AUTH_USER_MODEL


class CartItemManagerQuerySet(models.query.QuerySet):
    def update_total(self):
        return self.aggregate(Sum("total"))
    
    def update_vat(self):
        return self.aggregate(Sum("vat"))

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
    price_of_item = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    session_id = models.CharField(
        max_length=120,
        default=0,
        null=True,
        blank=True)
    total = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    vat = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    weight_in_grams = models.FloatField(default=0.00, max_length=2)
    meta_data = models.TextField(null=True, blank=True)

    objects = CartItemManager()

    def __str__(self):
        to_return = "Cart basket: " + str(self.id) + " - " + self.product.title
        return to_return
    
    def calculate_cart_item_vat(self):
        vat = (self.product.price * Decimal(self.product.vat_rate))*self.quantity
        print("calculate_cart_item_total - vat:", vat)
        return vat
    
    def calculate_cart_item_total(self):
        total = Decimal(0.00)
        total = self.quantity * Decimal(self.product.price)
        print("calculate_cart_item_total - total:", total)
        return total


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
        total = Decimal(0)
        vat = Decimal(0)
        sub_total = Decimal(0)
        shipping_cost = cart_obj.shipping
        for x in cart_obj.cart_items.all():
            vat += x.calculate_cart_item_vat()
            total += x.calculate_cart_item_total()
        if vat < 0.01:
            vat = 0
        sub_total = total + vat + shipping_cost
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
    total = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    vat = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    shipping = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    subtotal = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    weight_in_grams = models.FloatField(null=True, blank=True, default=0.00, max_length=2)
    meta_data = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)

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
