from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import api_home
from products.views import (
    ProductDestroyAPIView,
    ProductDetailAPIView,
    ProductListCreateAPIView,
    ProductUpdateAPIView
    )

app_name = 'api'

urlpatterns = [
    path('', api_home),
    path('auth/', obtain_auth_token),
    path('product/<int:pk>/update/', ProductUpdateAPIView.as_view(), name="api_product"),
    path('product/<int:pk>/delete/', ProductDestroyAPIView.as_view(), name="api_product"),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name="api_product"),
    path('product/', ProductListCreateAPIView.as_view(), name="api_product_create"),
]