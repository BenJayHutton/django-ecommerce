from rest_framework import authentication, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView
)

from api.mixins import StaffEditorPermissionMixin

from .models import Product
from .serializers import ProductSerializer


from api.authentication import TokenAuthentication

class ProductListCreateAPIView(
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
        serializer.save(description=description)

class ProductDetailAPIView(
    StaffEditorPermissionMixin,
    generics.RetrieveAPIView
    ):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductUpdateAPIView(
    StaffEditorPermissionMixin,
    generics.UpdateAPIView
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
        print("pk value", pk)
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

class ProductUpdateView(UpdateView):
    pass

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
        

class ProductDetailSlugView(DetailView):
    pass
