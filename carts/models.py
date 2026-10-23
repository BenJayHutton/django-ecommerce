from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from decimal import Decimal

from products.models import Product

User = settings.AUTH_USER_MODEL


class CartItemManagerQuerySet(models.query.QuerySet):
    def update_total(self):
        return self.aggregate(Sum("total"))

    def update_total_weight(self):
        return self.aggregate(Sum("weight_in_grams"))
   

class CartItemManager(models.Manager):

    def new_or_get(self, request, product_obj=None, product_quantity=None):
        created = False
        session_key = request.session.session_key
        obj = self.get_queryset().filter(
            session_key=session_key,
            product=product_obj,
            is_active=True,
        ).first()

        if obj is None:
            obj = self.model.objects.create(
                session_key=session_key,
                product=product_obj,
                quantity=product_quantity,
            )
            created = True
        return obj, created
    
    def total_weight_in_grams(self, request, *args, **kwargs):
        cart_item_weight_in_grams = kwargs.get("cart_item_weight_in_grams", 0)
        product_quantity = kwargs.get("product_quantity", 0)
        total = float(cart_item_weight_in_grams * product_quantity)
        return total

class CartItem(models.Model):
    product = models.ForeignKey(Product, default=None, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True)
    subtotal = models.DecimalField(default=Decimal(0), max_digits=12, decimal_places=4)
    vat = models.DecimalField(default=Decimal(0), max_digits=12, decimal_places=4)
    total = models.DecimalField(default=Decimal(0), max_digits=12, decimal_places=4)    
    weight_in_grams = models.FloatField(default=0.00, max_length=2)
    meta_data = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)    

    objects = CartItemManager()

    def __str__(self):
        return str(self.id)
    
    def calculate_cart_item_vat(self):
        self.vat = (Decimal(self.product.price)* Decimal(self.product.vat_rate))*self.quantity
        self.save()
        return self.vat
    
    def calculate_cart_item_subtotal(self, product_quantity):
        self.quantity = product_quantity
        self.subtotal = Decimal(self.quantity) * Decimal(self.product.price)
        self.save()
        return self.subtotal
    
    def weight_in_grams(self):
        self.weight_in_grams = self.product.weight_in_grams * self.quantity
        self.save()
        return float(self.weight_in_grams)


class CartManager(models.Manager):

    def new_or_get(self, request):
        session_key = request.session.session_key
        created = False
        cart_obj = self.get_queryset().filter(
            session_key=session_key,
            is_active=True,
        ).order_by('-id').first()

        if cart_obj is not None:
            if request.user.is_authenticated and cart_obj.user_id is None:
                cart_obj.user = request.user
                cart_obj.save(update_fields=['user'])
            elif request.user.is_authenticated:
                cart_obj.session_key = session_key
                cart_obj.save(update_fields=['session_key'])
        else:
            cart_obj = self.model.objects.create(session_key=session_key)
            created = True

        request.session['cart_id'] = cart_obj.id
        return cart_obj, created

    def calculate_cart_total(self, *args, **kwargs):
        cart_obj = kwargs.get("cart_obj", None)
        subtotal = Decimal(0)
        shipping_cost = Decimal(0)
        vat = Decimal(0)
        total = Decimal(0)
        for cart_item in cart_obj.cart_items.all():
            vat += cart_item.vat
            subtotal += cart_item.subtotal
        if vat < 0.01:
            vat = 0
        total = subtotal + shipping_cost + vat
        return subtotal, shipping_cost, vat, total

    def total_weight_in_grams(self, request, *args, **kwargs):
        cart_obj = kwargs.get("cart_obj", None)
        weight_in_grams = float(0.00)
        for x in cart_obj.cart_items.all():
            weight_in_grams += x.weight_in_grams
            x.save()
        return weight_in_grams

class Cart(models.Model):
    user = models.ForeignKey(User, default=None, null=True, blank=True, on_delete=models.SET_NULL)
    cart_items = models.ManyToManyField(CartItem, default=None, blank=True)
    session_key = models.CharField(max_length=255, default=None, null=True, blank=True)
    subtotal = models.DecimalField(default=Decimal(0), max_digits=12, decimal_places=4)
    shipping = models.DecimalField(default=Decimal(0), max_digits=12, decimal_places=4)
    vat = models.DecimalField(default=Decimal(0), max_digits=12, decimal_places=4)
    total = models.DecimalField(default=Decimal(0), max_digits=12, decimal_places=4)
    weight_in_grams = models.FloatField(null=True, blank=True, default=0, max_length=2)
    meta_data = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    def update_total(self, cart_item, currier):
        subtotal = Decimal(0)
        vat = Decimal(0)
        weight_in_grams = 0
        for item in self.cart_items.all():
            subtotal += item.subtotal
            vat += item.vat
            weight_in_grams += item.weight_in_grams()
        shipping_cost = Decimal(currier.get_price(weight=weight_in_grams))
        shipping_vat = shipping_cost*Decimal(0.2)
        vat+=shipping_vat
        self.weight_in_grams = weight_in_grams
        self.subtotal = subtotal
        self.shipping = shipping_cost
        self.vat = vat
        self.total = self.subtotal + self.shipping + self.vat
        self.save()
        currier.price = shipping_cost
        currier.weight = weight_in_grams
        currier.save()
        return  self.subtotal, self.shipping, self.vat, self.total
    
    @property
    def is_digital(self):
        qs = self.cart_items.all()
        for x in qs:
            if not x.product.is_digital:
                return False
        return True

    def get_absolute_url(self):
        return reverse("cart:detail", kwargs={'pk': self.pk})
