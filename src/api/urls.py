from django.urls import path

from .views import api_home
from products.views import (
    ProductDetailAPIView,
    ProductListCreateAPIView,
    product_alt_list_view
    )

app_name = 'api'

urlpatterns = [
    path('', api_home),
    path('product/<int:pk>/update/', ProductDetailAPIView.as_view(), name="api_product"),
    path('product/<int:pk>/delete/', ProductDetailAPIView.as_view(), name="api_product"),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name="api_product"),
    path('product/', ProductListCreateAPIView.as_view(), name="api_product_create"),
]