from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView
)

from analytics.mixins import ObjectViewedMixin
from carts.models import Cart

from .models import Product
from .forms import ProductForm


class ProductCreateView(CreateView):
    pass

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'products/create_product.html'
    form_class = ProductForm
    queryset = Product.objects.all()

    def get(self, *args, **kwargs):
        if not self.request.user.staff:
            return redirect("products:list")
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)

def product_delete_view(request, slug):
    pass

class ProductListView(ListView):
    template_name = "products/list.html"
    model = Product

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(ProductListView,self).get_context_data(
            *args,
            **kwargs)
        context['title'] = "Products"
        context['description'] = "Products for sale"
        return context
        

class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(
            ProductDetailSlugView,
            self).get_context_data(
            *
            args,
            **kwargs)
        slug = self.kwargs.get('slug')
        cart_obj, new_cart_obj = Cart.objects.new_or_get(request)
        cart_item_id = {}
        cart_item_obj = []
        for items in cart_obj.cart_items.all():
            cart_item_obj.append(items.product)
            cart_item_id[items.product] = int(items.id)
        try:
            product_obj = Product.objects.get(slug=slug)
        except BaseException:
            product_obj = None
        for items in cart_obj.cart_items.all():
            cart_item_id[items.product] = int(items.id)
        context = {
            "title": product_obj.title,
            "description": product_obj.description,
            'cart_obj': cart_obj,
            'product_obj': product_obj,
            'product_count': range(product_obj.quantity),
            'cart_item_id': cart_item_id,
            'cart_item_obj': cart_item_obj,
        }
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not found...")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.get(slug=slug, active=True)
            instance = qs.first()
        except BaseException:
            raise Http404("Product not found")
        return instance


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = "products/user-history.html"

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(
            UserProductHistoryView,
            self).get_context_data(
            *
            args,
            **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        cart_item_id = {}
        context['cart_obj'] = cart_obj
        context['cart_item_id'] = cart_item_id
        cart_item_obj = []
        for items in cart_obj.cart_items.all():
            cart_item_obj.append(items.product)
            cart_item_id[items.product] = int(items.id)
        context['cart_item_obj'] = cart_item_obj
        context['title'] = 'History'
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(
            Product, model_queryset=False)
        return views