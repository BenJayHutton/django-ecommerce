import datetime
from django.template.loader import get_template
from django.db import models
from django.db.models import Count, Sum, Avg
from django.urls import reverse
from django.utils import timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
from products.models import Product
from shipping.views import RoyalMail

import os

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)


class OrderManagerQuerySet(models.query.QuerySet):
    def recent(self):
        return self.order_by("-updated", "-timestamp")

    def get_sales_breakdown(self):
        recent = self.recent().not_refunded()
        recent_data = recent.totals_data()
        recent_cart_data = recent.cart_data()
        shipped = recent.not_refunded().by_status(status='shipped')
        shipped_data = shipped.totals_data()
        paid = recent.by_status(status='paid')
        paid_data = paid.totals_data()
        data = {
            'recent': recent,
            'recent_data': recent_data,
            'recent_cart_data': recent_cart_data,
            'shipped': shipped,
            'shipped_data': shipped_data,
            'paid': paid,
            'paid_data': paid_data,
        }
        return data

    def by_weeks_range(self, weeks_ago=1, number_of_weeks=1):
        if number_of_weeks > weeks_ago:
            number_of_weeks = weeks_ago
        days_ago_start = weeks_ago * 7
        days_ago_end = days_ago_start - (number_of_weeks * 7)
        start_date = timezone.now() - datetime.timedelta(days=days_ago_start)
        end_date = timezone.now() - datetime.timedelta(days=days_ago_end)
        return self.by_range(start_date=start_date, end_date=end_date)

    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(updated__gte=start_date)
        return self.filter(
            updated__gte=start_date).filter(
            updated__lte=end_date)

    def by_date(self):
        now = timezone.now().date() - datetime.timedelta(days=7)
        return self.filter(updated__date__gte=now)

    def totals_data(self):
        return self.aggregate(Sum("total"), Avg("total"))

    def cart_data(self):
        return self.aggregate(
            Sum("cart__cart_items__total"),
            Avg("cart__cart_items__total"),
            Count("cart__cart_items__quantity"))

    def by_status(self, status='shipped'):
        return self.filter(status=status)

    def not_refunded(self):
        return self.exclude(status='refunded')

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)

    def not_created(self):
        return self.exclude(status='created')


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(
            billing_profile=billing_profile,
            cart=cart_obj,
            active=True,
            status='created')
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(
                billing_profile=billing_profile, cart=cart_obj)
            created = True
        return obj

    def email_order(self, order_id):
        qs = self.get_queryset().filter(order_id=order_id)
        for order in qs:
            subject = "SweetSweetSwag.com, order confirmation: " + order.order_id
            try:
                cus_name = order.billing_profile.user.full_name
            except BaseException:
                cus_name = ""
            order_id = order.order_id
            cus_email = order.billing_profile.email
            cus_items = ""
            for cart_items in order.cart.cart_items.all():
                cus_items = cus_items + \
                    str(cart_items.quantity) + "* " + \
                    cart_items.product.title + "\n"
            order_tax = order.tax
            order_shipping = order.shipping_total
            order_total = order.total
            order_subtotal = order.sub_total
        context = {
            'name': cus_name,
            'order_id': order_id,
            'cus_items': cus_items,
            'order_tax': order_tax,
            'order_shipping': order_shipping,
            'order_total': order_total,
            'order_subtotal': order_subtotal,
        }
        txt_ = get_template(
            "order_email/emails/order_confirmation.txt").render(context)
        html_ = get_template(
            "order_email/emails/order_confirmation.html").render(context)
        recipient_list = [cus_email]

        message = Mail(
            from_email='no-reply@sweetsweetswag.com',
            to_emails=cus_email,
            subject=subject,
            html_content=html_)
        try:
            sg = SendGridAPIClient(os.environ.get('EMAIL_HOST_PASSWORD'))
            response = sg.send(message)
        except Exception as e:
            print(e)
        return True
    
    def email_order_shipped(self,order_id):
        qs = self.get_queryset().filter(order_id=order_id)
        for order in qs:
            if order.status =="shipped":
                subject = "SweetSweetSwag.com, your order: " + order.order_id + " has been shipped."
                try:
                    cus_name = order.billing_profile.user.full_name
                except BaseException:
                    cus_name = ""
                order_id = order.order_id
                cus_email = order.billing_profile.email

        context = {
            'name': cus_name,
            'order_id': order_id,
        }
        txt_ = get_template(
            "order_email/emails/order_shipped.txt").render(context)
        html_ = get_template(
            "order_email/emails/order_shipped.html").render(context)
        recipient_list = [cus_email]
        message = Mail(
            from_email='no-reply@sweetsweetswag.com',
            to_emails=cus_email,
            subject=subject,
            html_content=html_)
        try:
            sg = SendGridAPIClient(os.environ.get('EMAIL_HOST_PASSWORD'))
            response = sg.send(message)
        except Exception as e:
            print(e)
        return True


class Order(models.Model):
    billing_profile = models.ForeignKey(
        BillingProfile,
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    order_id = models.CharField(
        max_length=120,
        unique=True,
        blank=True,
        null=True)
    shipping_address = models.ForeignKey(
        Address,
        default=None,
        related_name='shipping_address',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    billing_address = models.ForeignKey(
        Address,
        default=None,
        related_name='billing_address',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    cart = models.ForeignKey(
        Cart,
        default=None,
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=120,
        default='created',
        choices=ORDER_STATUS_CHOICES)
    total = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    tax = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    shipping_total = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    sub_total = models.DecimalField(default=0.00, max_digits=33, decimal_places=28)
    active = models.BooleanField(default=True)
    meta_data = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})

    def get_status(self):
        if self.status == "refunded":
            return "Refunded Order"
        elif self.status == "shipped":
            return "Shipped"
        return "Shipping Soon"

    def __str__(self):
        return self.order_id

    def update_total(self, *args, **kwargs):
        royal_mail_obj = RoyalMail
        total_weight_in_grams = None #kwargs['weight_in_grams']
        shipping_cost = royal_mail_obj.get_shipping_cost(
        royal_mail_obj, total_weight_in_grams)
        try:
            self.total = self.cart.total
            self.shipping_total = shipping_cost
            self.tax = self.cart.vat
            self.sub_total = self.cart.subtotal
            self.save()
        except Exception as e:
            print(e)

        return self.sub_total

    def new_or_get_order(self, *args, **kwargs):
        product_id = kwargs['product_id']
        product_qty = kwargs['product_qty']
        session_order_id = kwargs['session_order_id']
        test_obj = Order(order_id=session_order_id)
        test_obj.save()
        obj = Order.objects.filter(order_id__exact=1)

    def check_done(self):
        shipping_address_required = not self.cart.is_digital
        shipping_done = False
        if shipping_address_required and self.shipping_address:
            shipping_done = True
        elif shipping_address_required and not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True
        billing_profile = self.billing_profile
        billing_address = self.billing_address
        total = self.total
        if billing_profile and shipping_done and billing_address and total >= 0:
            return True
        return False

    def update_purchases(self):
        for p in self.cart.cart_items.all():
            obj, create = ProductPurchase.objects.get_or_create(
                order_id=self.order_id,
                product=p.product,
                billing_profile=self.billing_profile,
            )
        return ProductPurchase.objects.filter(order_id=self.order_id).count()

    def mark_paid(self):
        if self.status != 'paid':
            if self.status != 'paid':
                if self.check_done():
                    self.status = "paid"
                    self.save()
                    self.update_purchases()
        return self.status


class ProductPurchaseQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(refunded=False)

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)

    def digital(self):
        return self.filter(product__is_digital=True)


class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def digital(self):
        return self.get_queryset().active().digital()

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def products_by_id(self, request):
        qs = self.by_request(request).digital()
        ids_ = [x.product.id for x in qs]
        return ids_

    def products_by_request(self, request):
        ids_ = self.products_by_id(request)
        products_qs = Product.objects.filter(id__in=ids_).distinct()
        return products_qs


class ProductPurchase(models.Model):
    order_id = models.CharField(max_length=120)
    billing_profile = models.ForeignKey(
        BillingProfile, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    refunded = models.BooleanField(default=False)
    meta_data = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title
