from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView
)

class ProductCreateView(CreateView):
    pass

class ProductUpdateView(UpdateView):
    pass

def product_delete_view(request, slug):
    pass

class ProductListView(ListView):
    pass

class ProductDetailSlugView(DetailView):
    pass
