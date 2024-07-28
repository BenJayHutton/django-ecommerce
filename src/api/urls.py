from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import api_home
from products.views import (
    ProductDestroyAPIView,
    ProductDetailAPIView,
    ProductListCreateAPIView,
    ProductUpdateAPIView
    )
from search.views import(
    SearchApiProductView,
)

app_name = 'api'

urlpatterns = [
    path('', api_home, name="home"),
    path('auth/', obtain_auth_token, name="auth"),
    path('product/<int:pk>/update/', ProductUpdateAPIView.as_view(), name="product-update"),
    path('products/<int:pk>/update/', ProductUpdateAPIView.as_view(), name="products-update"),
    path('product/<int:pk>/delete/', ProductDestroyAPIView.as_view(), name="product-delete"),
    path('products/<int:pk>/delete/', ProductDestroyAPIView.as_view(), name="products-delete"),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name="product-detail"),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name="products-detail"),
    path('product/', ProductListCreateAPIView.as_view(), name="product_create"),
    path('products/', ProductListCreateAPIView.as_view(), name="products_create"),
    path('search/', SearchApiProductView.as_view(), name='search'),
]