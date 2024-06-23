from rest_framework import generics
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView
)
from .models import Product
from .serializers import ProductSerializer

class ProductCreateAPIView(generics.CreateAPIView):
    ueryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        # serializer.save(user=request.user.user)
        print("serializer", serializer)
        serializer.save()

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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
