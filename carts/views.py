import logging
import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DetailView, View

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.forms import AddressForm
from addresses.models import Address
from billing.models import BillingProfile
from orders.models import Order
from products.models import Product
from currier.models import Currier as CurrierModel

from .models import Cart, CartItem
from .forms import CartForm

STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", None)
now = timezone.now()

project_debug_log = logging.getLogger("project_debug_log")
project_access_log = logging.getLogger("project_access_log")

class CartHomeView(View):

    form_class = CartForm
    queryset = Cart.objects.all()

    def get(self, request):
        cart_obj, cart_obj_created = Cart.objects.new_or_get(request)
        request.session["cart_id"] = cart_obj.id
        context = {
            "title": "Cart",
            "description": "Checkout home",
            "cart_obj": cart_obj,
        }
        return render(request, "carts/home.html", context)
    
    def post(self, request):
        cart_item_add = request.POST.get('cart_item_add', False)
        cart_item_update = request.POST.get('cart_item_update', False)
        cart_item_remove = request.POST.get('cart_item_remove', False)        
        product_quantity = request.POST.get('product-quantity', False)        
        is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

        if is_ajax:
            json_data={}
            if cart_item_add:
                json_data = self.add_to_cart(request)
            if cart_item_update:
                json_data = self.update_cart(request)
            if cart_item_remove:
                json_data = self.delete_cart(request)
            json_string = json.dumps(json_data)
            return HttpResponse(json_string)
        
        if cart_item_add:
            self.add_to_cart(request)
            print("CartHomeView,self.add_to_cart(request)")
        if cart_item_update:
            self.update_cart(request)
        if cart_item_remove:
            self.delete_cart(request)
        return redirect("cart:home")
    
    def add_to_cart(self, request):
        print("CartHomeView, def add_to_cart(request)")
        session_obj = request.session
        cart_id = session_obj["cart_id"]
        product_quantity = int(request.POST.get('product-quantity'))
        product_id = request.POST.get("product_id")
        json_data = {}
        try:
            product_obj = Product.objects.get(id=product_id)
        except Exception as E:
            project_debug_log.debug(f'[{now}] CartHomeView.add_to_cart: error getting product_obj {type(E)} - {E}')

        try:
            cart_obj, cart_obj_created = Cart.objects.new_or_get(request)
        except Exception as E:
           project_debug_log.debug(f'[{now}] CartHomeView.add_to_cart: error getting cart_obj {type(E)} - {E}')

        try:
            currier_obj, currier_obj_created = CurrierModel.objects.new_or_get(request, cart=cart_obj)
        except Exception as E:
            project_debug_log.debug(f"[{now}] CartHomeView: error getting currier_obj raised {type(E)} - {E}")

        try:
            cart_item_obj, cart_item_obj_created = CartItem.objects.new_or_get(request, product_obj=product_obj, product_quantity=product_quantity)
            print(f"cart item add to cart obj {type(cart_item_obj)} {cart_item_obj}")
            
            cart_item_id = cart_item_obj.id
            cart_item_price = cart_item_obj.total
            cart_obj.cart_items.add(cart_item_obj)
            cart_item_obj.calculate_cart_item_subtotal(product_quantity=product_quantity)
            cart_item_obj.calculate_cart_item_vat()
            cart_obj.update_total(cart_item=cart_item_obj, currier=currier_obj)
            request.session['cart_item_count'] = cart_obj.cart_items.count()
        except Exception as E:
            project_debug_log.exception(f'[{now}] CartHomeView.add_to_cart: error getting cart_item_obj {type(E)} - {E}')        
        json_data = {
                    "cart_item_id": cart_item_id,
                    "cart_item_price": float(cart_item_price),
                    "cart_id": cart_id,
                    "cart_item_add":True,
                    "total": float(cart_obj.total),
                    "vat": float(cart_obj.vat),
                    "shipping": float(cart_obj.shipping),
                    "sub_total": float(cart_obj.subtotal),
                    "cart_item_count": cart_obj.cart_items.count()
                }
        return json_data

    def update_cart(self, request):
        session_obj=request.session
        product_quantity = int(request.POST.get('product_quantity', 0))
        product_id = request.POST.get("product_id", None)
        product_obj = Product.objects.get(id=product_id)
        cart_id = session_obj["cart_id"]
        cart_item_id = request.POST.get('cart_item_id', None)
        cart_obj = get_object_or_404(Cart, pk=cart_id)
        cart_item_obj = cart_item_obj, cart_item_obj_created = CartItem.objects.new_or_get(request, product_obj=product_obj, product_quantity=product_quantity)
        try:
            currier_obj, currier_obj_created = CurrierModel.objects.new_or_get(request, cart=cart_obj)
            cart_item_obj.calculate_cart_item_subtotal(product_quantity=product_quantity)
            cart_item_obj.calculate_cart_item_vat()
            print(f"update cart, currier_obj {type(currier_obj)} {currier_obj}")
            cart_obj.update_total(cart_item=cart_item_obj, currier=currier_obj)
            request.session['cart_item_count'] = cart_obj.cart_items.count()
        except Exception as E:
            project_debug_log.debug(f'[{now}] CartHomeView update: error raised {type(E)} - {E}')
            raise
        
        json_data = {
            "cart_id": int(cart_id),
            "cart_item_id": int(cart_item_id),
            "cart_item_price": float(cart_item_obj.total),
            "cart_item_updated":True,
            "total": float(cart_obj.total),
            "vat": float(cart_obj.vat),
            "shipping": float(cart_obj.shipping),
            "sub_total": float(cart_obj.subtotal),
            "cart_item_count": cart_obj.cart_items.count()
        }
        return json_data
    
    def delete_cart(self, request):
        cart_obj, cart_obj_created = Cart.objects.new_or_get(request)
        cart_item_id = request.POST.get('cart_item_id', None)
        product_quantity = int(request.POST.get('product_quantity', 0))        
        cart_item_obj = CartItem.objects.get(id=cart_item_id)
        cart_obj.cart_items.remove(cart_item_obj)
        try:
            currier_obj, currier_obj_created = CurrierModel.objects.new_or_get(request, cart=cart_obj)
            cart_item_obj.calculate_cart_item_subtotal(product_quantity=product_quantity)
            cart_item_obj.calculate_cart_item_vat()
            request.session['cart_item_count'] = cart_obj.cart_items.count()
        except Exception as E:
            project_debug_log.debug(f'[{now}] CartHomeView delete: error raised {type(E)} - {E}')
        return cart_obj


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
        context = super(CartDetailView, self).get_context_data(*args, **kwargs)
        context['title'] = "Cart Details"
        return context

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        qs = Cart.objects.get(id=pk)
        if qs:
            return qs
        raise Http404


def checkout_home(request, *args, **kwargs):
    currier_obj = None
    if request.method == 'POST':
        request.session["email_obj"] = request.POST.get("email")
    email_obj = request.session.get("email_obj")
    session_key = request.session.session_key
    user_obj = request.user
    order_obj = None
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)
    shipping_address_required = not cart_obj.is_digital
    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressForm
    address_qs = None
    has_card = False
    
    if cart_created or cart_obj.cart_items.count() == 0:
        redirect("cart:home")
    
    if user_obj.is_authenticated:
        email_obj = user_obj.email
    else:
        if email_obj:
            GuestEmail.objects.new_or_get(request, email=email_obj)
    
    if email_obj:
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request, email=email_obj)
    else:
        billing_profile = None
    
    # bind forms to POST if present (handle guest checkout even if no billing_profile exists yet)
    if request.method == 'POST':
        login_form = LoginForm(request=request, data=request.POST)
        guest_form = GuestForm(request=request, data=request.POST)
        try:
            if guest_form.is_valid():
                guest_obj = guest_form.save()
                email_val = guest_obj.email
                GuestEmail.objects.new_or_get(request, email=email_val)
                billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request, email=email_val)
                request.session['customer_email'] = email_val
        except Exception as E:
            print(f"Error with form {type(E)}: {E}")
        try:
            if login_form.is_valid():
                billing_profile, _ = BillingProfile.objects.new_or_get(request)
                if request.user.is_authenticated:
                    billing_profile.email = request.user.email
                    billing_profile.user = request.user
                    billing_profile.save()
        except Exception as E:
            print(f"error raised while updating billing profile {type(E)}: {E}")

    if billing_profile is not None:
        if user_obj.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        else:
            address_qs = None
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj, session_key=session_key)
        request.session['order_obj'] = order_obj.order_id
        order_obj.total = cart_obj.total
        order_obj.vat = cart_obj.vat
        order_obj.shipping_total = cart_obj.shipping
        order_obj.subtotal = cart_obj.subtotal
        order_obj.save()
        
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
        if billing_address_id or shipping_address_id:
            order_obj.save()
    context = {
        "address_form": address_form,
        "address_qs": address_qs,
        "billing_profile": billing_profile,
        "currier_obj":currier_obj,
        "description": "Cart home",
        "guest_form": guest_form,
        "email_obj": email_obj,
        "login_form": login_form,
        "object": order_obj,
        "publish_key": STRIPE_PUB_KEY,
        "shipping_address_required": shipping_address_required,
        "title": "Cart",
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
        if key =='cart_id':
            cart_obj = Cart.objects.get(id=value)
            cart_obj.is_active=False
            cart_obj.save()
    for session_key in (
        'order_obj',
        'cart_item_id',
        'shipping_address_id',
        'billing_address_id',
        'cart_id',
    ):
        match session_key:
            case 'order_obj' | 'cart_item_id' | 'shipping_address_id' | 'billing_address_id' | 'cart_id':
                request.session.pop(session_key, None)
    request.session['cart_item_count'] = 0
    return render(request, "carts/checkout-done.html", context)
