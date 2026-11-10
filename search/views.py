import logging
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView

from products.models import Product
from tags.models import Tag

now = timezone.now()
project_error_log = logging.getLogger("project_error_log")


class SearchProductView(ListView):
    template_name = "search/view.html"

    def get_context_data(self, *args, **kwargs):
        try:
            query = self.request.GET.get('query')
            context = super(SearchProductView, self).get_context_data(*args, **kwargs)
            context['query'] = query
            return context
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] SearchProductView get_context_data\n{type(e)} {e}', exc_info=True)
            return JsonResponse({"Error": str(e)}, status=400)

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
        try:
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
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] SearchTagView GET\n{type(e)} {e}', exc_info=True)
            return JsonResponse({"Error": str(e)}, status=400)
