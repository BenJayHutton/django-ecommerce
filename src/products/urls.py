from django.urls import path
from .views import (
    ProductCreateView,
    ProductUpdateView,
    product_delete_view,
    ProductListView,
    ProductDetailSlugView
    )

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('create/', ProductCreateView.as_view(), name='create'),
    path('delete/<slug:slug>/', product_delete_view, name='delete'),
    path('update/<slug:slug>/', ProductUpdateView.as_view(), name='update'),
    path('<slug:slug>/', ProductDetailSlugView.as_view(), name='slug'),
]