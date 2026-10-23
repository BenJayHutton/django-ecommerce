from django.urls import path, re_path
from .views import (
    CartHomeView,
    CartCreateView,
    CartDetailView,
    cart_delete_view,
    checkout_home,
    checkout_done_view,
    )

urlpatterns = [
    path('', CartHomeView.as_view(), name='home'),
    path('create/', CartCreateView.as_view(), name='create'),
    re_path('delete/(?P<pk>[0-9A-Za-z]+)/', cart_delete_view, name='delete'),
    re_path('detail/(?P<pk>[0-9A-Za-z]+)/', CartDetailView.as_view(), name='detail'),
    path('checkout/', checkout_home, name='checkout'),
    path('checkout/success/', checkout_done_view, name='success')
]
