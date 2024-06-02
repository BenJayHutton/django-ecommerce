from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView
)
from .models import Product

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
        return context
        

class ProductDetailSlugView(DetailView):
    pass
