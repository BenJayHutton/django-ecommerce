from django.urls import path

from .views import api_home
from products.views import (
    ProductDetailAPIView,
    ProductCreateAPIView,
    )

app_name = 'api'

urlpatterns = [
    path('', api_home),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name="api_product"),
    path('products/', ProductCreateAPIView.as_view(), name="api_product_create"),
]