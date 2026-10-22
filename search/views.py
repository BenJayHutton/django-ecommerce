from django.shortcuts import render
from django.views.generic import ListView

from products.models import Product, Tag
from products.serializers import ProductSerializer

from rest_framework import generics
from rest_framework.response import Response

class SearchApiProductView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        user = None
        if request.user.is_authenticated:
            user = request.user.username
        query = request.GET.get('q')
        public = str(request.GET.get('public')) !="0"
        tags = request.GET.get('tags') or None
        if not query:
            return Response('', status=400)
        results = None
        return Response(results)

class OldSearchApiProductView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        q = self.request.GET.get('q')
        user = None
        results = Product.objects.none()
        if q is not None:
            if self.request.user.is_authenticated:
                user = self.request.user
            results = qs.search(q, user=user)
        return results

class SearchProductView(ListView):
    template_name = "search/view.html"

    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductView, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        product_search = Product.objects.search(query)        
        context['q'] = product_search
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        query = method_dict.get('q', None)
        return Product.objects.search(query)
