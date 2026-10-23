from django.http import HttpResponse
from django.views.generic import ListView
from django.shortcuts import render
from products.models import Product
from tags.models import Tag
import json


class SearchProductView(ListView):
    template_name = "search/view.html"

    def get_context_data(self, *args, **kwargs):
        query = self.request.GET.get('query')
        context = super(SearchProductView, self).get_context_data(*args, **kwargs)
        context['query'] = query
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        query = method_dict.get('query', None)
        if query is not None:
            return Product.objects.search(query)
        else:
            return Product.objects.all()


class SearchTagView(ListView):
    template_name = "search/tag_view.html"

    def get(self, request, *args, **kwargs):
        request = self.request
        tag_obj = ["Film","Books","Trading Cards"]
        tag = request.GET.get("tag")
        sub_tag_obj = Tag.sub_tag(sub_tag=tag)
        product_by_tag = Product.objects.search_tag(tag)
        context = {
            "product_list": product_by_tag,
            "sub_tag_obj": sub_tag_obj,
            "tag_obj": tag_obj
        }
        return render(request,"search/tag_view.html", context)
