from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    View
)

from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressForm
from addresses.models import Address
from billing.models import BillingProfile
from orders.models import Order
from payment.views import StripeCharge
from products.models import Product
from shipping.views import RoyalMail
from .models import Cart, CartItem
from .forms import CartForm, CartItemForm

import json
import stripe
import os

STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", None)


class CartCreateView(LoginRequiredMixin, CreateView):
    template_name = 'carts/create_cart.html'
    form_class = CartForm
    queryset = Cart.objects.all()

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CartUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'orders/create_order.html'
    form_class = CartForm
    queryset = Cart.objects.all()

    def get(self, *args, **kwargs):
        if not self.request.user.staff:
            return redirect("home")
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)


def cart_delete_view(request, pk):
    obj = get_object_or_404(Cart, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect('analytics:carts')
    context = {
        "object": obj
    }
    return render(request, "carts/delete_cart.html", context)


class CartDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = "carts/detail.html"

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(
            CartDetailView,
            self).get_context_data(
            *
            args,
            **kwargs)
        context['title'] = "Cart Details"
        return context

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        qs = Cart.objects.get(id=pk)
        if qs:
            return qs
        raise Http404


class CartHome(ListView):
    template_name = "carts/home.html"

    def get(self, request):
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context = {
            "cart_obj": cart_obj,
            "title": "Cart",
            "description": "Checkout home",
        }
        return render(request, "carts/home.html", context)

class UpdateCart(View):
    form_class = CartItemForm
    queryset = CartItem.objects.all()

    def get(request):
        pass

    def post(request):
        pass


def cart_update(request, *args, **kwargs):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    item_added = False
    item_removed = False
    item_updated = False
    cart_item_id = request.POST.get('cart_item_id', None)
    cart_item_update = request.POST.get('cart_item_update', False)
    product_item_remove = request.POST.get('product_item_remove', False)
    cart_item_remove = request.POST.get('cart_item_remove', False)
    cart_item_add = request.POST.get('cart_item_add', False)
    cart_item_weight_in_grams = float(request.POST.get('weight_in_grams', None))

    if cart_item_add is False:
        cart_item_add = request.POST.get('cartItemAdd', False)

    if cart_item_update is False:
        cart_item_update = request.POST.get('cartItemUpdate', False)

    if product_item_remove is False:
        product_item_remove = request.POST.get('cartItemRemove', False)

    if cart_item_remove is False:
        cart_item_remove = request.POST.get('cartItemRemove', False)

    product_id = request.POST.get("product_id", None)
    product_quantity = int(request.POST.get('product_quantity', 0))
    try:
        product_obj = Product.objects.get(id=product_id)
    except BaseException:
        product_obj = False

    if product_obj:
        cart_obj, new_obj = Cart.objects.new_or_get(request)

        if product_item_remove or cart_item_remove:
            cart_item_obj = CartItem.objects.get(id=cart_item_id)
            cart_obj.cart_items.remove(cart_item_obj)
            total, vat, sub_total = Cart.objects.calculate_cart_total(
                request, cart_obj=cart_obj)
            weight_in_grams = float(CartItem.objects.total_weight_in_grams(
                    request, cart_item_obj=cart_item_obj,
                    cart_item_weight_in_grams=cart_item_weight_in_grams,
                    product_quantity=product_quantity))
            cart_obj.total = total
            cart_obj.vat = vat
            cart_obj.subtotal = sub_total
            cart_obj.weight_in_grams = weight_in_grams
            cart_obj.save()
                

            item_removed = True
            request.session['cart_item_count'] = cart_obj.cart_items.count()

        if cart_item_update:
            cart_item_obj = CartItem.objects.get(id=cart_item_id)
            if product_quantity != cart_item_obj.quantity:
                cart_item_obj.quantity = product_quantity
                weight_in_grams = float(CartItem.objects.total_weight_in_grams(
                    request, cart_item_obj=cart_item_obj,
                    cart_item_weight_in_grams=cart_item_weight_in_grams,
                    product_quantity=product_quantity))
                cart_item_obj.save()

                total, vat, sub_total = Cart.objects.calculate_cart_total(
                    request, cart_obj=cart_obj)
                
                if total and vat and sub_total:
                    cart_obj.total = total
                    cart_obj.vat = vat
                    cart_obj.subtotal = sub_total
                    cart_obj.save()
            item_updated = True

        if cart_item_add:
            cart_item_obj, new_item_obj = CartItem.objects.new_or_get(
                request, product_obj=product_obj)
            cart_item_obj.quantity = product_quantity
            weight_in_grams = float(CartItem.objects.total_weight_in_grams(
                request, cart_item_obj=cart_item_obj,
                cart_item_weight_in_grams=cart_item_weight_in_grams,
                product_quantity=product_quantity))
            cart_item_obj.save()
            cart_obj.cart_items.add(cart_item_obj)
            cart_item_id = cart_item_obj.id
            total, vat, sub_total = Cart.objects.calculate_cart_total(
                request, cart_obj=cart_obj)
            weight_in_grams = float(Cart.objects.total_weight_in_grams(
                request, cart_obj=cart_obj))
            if total and vat and sub_total:
                cart_obj.total = total
                cart_obj.vat = vat
                cart_obj.subtotal = sub_total
                cart_obj.save()
            item_added = True
        request.session['cart_item_count'] = cart_obj.cart_items.count()

        if is_ajax:
            json_data = {
                "added": item_added,
                "removed": item_removed,
                "updated": item_updated,
                "cartItemCount": cart_obj.cart_items.count(),
                "cartWeight": cart_obj.weight_in_grams,
                "cart_shipping": cart_obj.shipping,
            }
            if cart_item_id:
                json_data.update({
                    "cart_item_id": cart_item_id
                })
            if product_obj:
                json_data.update({
                    "productQty": product_obj.quantity
                })
            if item_added:
                json_data.update({
                    "inCartUrl": reverse("cart:home")
                })
            if item_updated or item_removed:
                json_data.update({
                    "cart_total": round(cart_obj.total, 2),
                    "cart_vat": round(cart_obj.vat, 2),
                    "cart_shipping": round(cart_obj.shipping, 2),
                    "price_of_item": round(cart_item_obj.total, 2),
                    "cart_subtotal": round(cart_obj.subtotal, 2),
                })
            return JsonResponse(json_data)
    return redirect("cart:home")


def checkout_home(request, *args, **kwargs):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    did_charge = False
    if cart_created or cart_obj.cart_items.count() == 0:
        redirect("cart:home")

    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressForm
    billing_address_id = request.session.get("billing_address_id", None)

    shipping_address_required = not cart_obj.is_digital

    shipping_address_id = request.session.get("shipping_address_id", None)
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(
        request)
    address_qs = None
    has_card = False

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(
                billing_profile=billing_profile)
        order_obj = Order.objects.new_or_get(billing_profile, cart_obj)
        request.session['order_obj'] = order_obj.order_id
        order_obj.shipping_total = cart_obj.shipping
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(
                id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(
                id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()
        has_card = billing_profile.has_card
        
    context = {
        "title": "Cart",
        "description": "Cart home",
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
        "shipping_address_required": shipping_address_required,
    }
    return render(request, "carts/checkout.html", context)


def checkout_done_view(request):
    context = {
        "title": "Thank you"
    }
    for key, value in request.session.items():
        if key == 'order_obj':
            order_obj = Order.objects.get(order_id=value)
            context["order_obj"] = order_obj
            order_complete = Order.objects.email_order(value)
    if 'order_obj' in request.session:
        del request.session['order_obj']
    try:
        del request.session['cart_id']
        request.session['cart_item_count'] = 0
    except:
        pass
    return render(request, "carts/checkout-done.html", context)
