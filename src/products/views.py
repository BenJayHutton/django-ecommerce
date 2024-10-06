from rest_framework import authentication, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView
)

from api.mixins import (
    StaffEditorPermissionMixin,
    UserQuerySetMixin
    )

from analytics.mixins import ObjectViewedMixin
from carts.models import Cart

from .models import Product
from .serializers import ProductSerializer
from .forms import ProductForm


from api.authentication import TokenAuthentication

class ProductListCreateAPIView(
    UserQuerySetMixin,
    StaffEditorPermissionMixin,
    generics.ListCreateAPIView
    ):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description') or None
        if description is None:
            description = title
        serializer.save(user=self.request.user, description=description)


class ProductDetailAPIView(
    StaffEditorPermissionMixin,
    generics.RetrieveAPIView
    ):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductUpdateAPIView(
    StaffEditorPermissionMixin,
    generics.RetrieveUpdateAPIView
    ):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()
        if not instance.description:
            instance.description = instance.title


class ProductDestroyAPIView(
    StaffEditorPermissionMixin,
    generics.DestroyAPIView
    ):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        # instance
        super().perform_destroy(instance)



@api_view(['GET', 'POST'])
def product_alt_list_view(request, pk=None, *args, **kwargs):
    method = request.method

    if method == 'GET':
        if pk is not None:
            # detail view
            obj = get_object_or_404(Product, pk=pk)
            data = ProductSerializer(obj, many=False).data
            return Response(data)
        queryset = Product.objects.all()
        data = ProductSerializer(queryset, many=True).data
        return Response(data)
    if method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data.get('title')
            description = serializer.validated_data.get('description')
            if description is None:
                description = title
            serializer.save(description=description)
            return Response(serializer.data)
        else:
            return Response({"error":serializer.errors})


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
