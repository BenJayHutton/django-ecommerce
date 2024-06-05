from django.shortcuts import render
from django.views.generic import ListView

from products.models import Product, Tag


class SearchProductView(ListView):
    template_name = "search/view.html"

    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductView, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('query')
        product_search = Product.objects.search(query)        
        context['query'] = product_search
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        query = method_dict.get('query', None)
        return Product.objects.search(query)
