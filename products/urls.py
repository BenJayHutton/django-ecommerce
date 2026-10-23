from django.urls import path, re_path

from .views import (
    ProductCreateView,
    ProductDetailSlugView,
    ProductDownloadView,
    ProductListView,
    ProductUpdateView,
    product_delete_view,
)

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('create/', ProductCreateView.as_view(), name='create'),
    path('delete/<slug:slug>/', product_delete_view, name='delete'),
    path('update/<slug:slug>/', ProductUpdateView.as_view(), name='update'),
    path('<slug:slug>/', ProductDetailSlugView.as_view(), name='detail'),
    re_path('(?P<slug>[\w-]+)/(?P<pk>\d+)/', ProductDownloadView.as_view(), name='download'),
]
