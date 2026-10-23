from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    View
)

from analytics.mixins import ObjectViewedMixin
from carts.models import Cart
from orders.models import ProductPurchase
from tags.models import Tag

from .models import Category, Product, ProductFile
from .forms import ProductForm


class ProductCreateView(LoginRequiredMixin, CreateView):
    template_name = 'products/create_product.html'
    form_class = ProductForm
    queryset = Product.objects.all()

    def get(self, *args, **kwargs):
        if not self.request.user.staff:
            return redirect("products:list")
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)


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
    obj = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        obj.delete()
        return redirect('analytics:products')
    context = {
        "object": obj
    }
    return render(request, "blog/delete_blog.html", context)


class ProductListView(ListView):
    template_name = "products/list.html"
    model = Product

    def get_context_data(self, **kwargs):
        request = self.request
        context = super(ProductListView, self).get_context_data(**kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        cart_item_id = {}
        cart_item_obj = []
        for items in cart_obj.cart_items.all():
            cart_item_obj.append(items.product)
            cart_item_id[items.product] = int(items.id)
        shop_tags = ["Film","Books","Trading Cards"]
        tag_obj = Tag.objects.filter(name__in=shop_tags)
        context['cart_item_id'] = cart_item_id
        context['cart_item_obj'] = cart_item_obj
        context['cart_obj'] = cart_obj
        context["categories"] = Category.objects.all()
        context['description'] = "Products for sale"
        context['tag_obj'] =  tag_obj
        context['title'] = "Products"
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = Product.objects.filter(active=True)
        category_slug = self.request.GET.get("General")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = "products/user-history.html"

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super( UserProductHistoryView, self).get_context_data(*args, **kwargs)
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


class ProductDownloadView(View):
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug)
        if downloads_qs.count() != 1:
            raise Http404("Download not found")
        download_obj = downloads_qs.first()
        # permission check
        can_download = False
        user_ready = True

        if download_obj.user_required:
            if not request.user.is_authenticated:
                user_ready = False
            else:
                can_download = False

        purchased_products = Product.objects.none()
        if download_obj.free:
            can_download = True
            user_ready = True
        else:
            purchased_products = ProductPurchase.objects.products_by_request(
                request)
            if download_obj.product in purchased_products:
                can_download = True

        if not can_download or not user_ready:
            messages.error(request, "You don't have access to download media")
            return redirect(download_obj.get_default_url())

        aws_filepath = download_obj.generate_download_url()
        return HttpResponseRedirect(aws_filepath)


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
