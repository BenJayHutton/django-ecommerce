from django.urls import path, re_path
from .views import (
    CartHome,
    CartCreateView,
    CartDetailView,
    CartUpdateView,
    cart_delete_view,
    cart_update, 
    checkout_home,
    checkout_done_view,
    )

app_name = 'cart'

urlpatterns = [
    path('', CartHome.as_view(), name='home'),
    path('create/', CartCreateView.as_view(), name='create'),
    re_path(r'^update_cart/(?P<pk>[0-9A-Za-z]+)/$', CartUpdateView.as_view(), name='update_cart'),
    re_path('delete/(?P<pk>[0-9A-Za-z]+)/', cart_delete_view, name='delete'),
    re_path('detail/(?P<pk>[0-9A-Za-z]+)/', CartDetailView.as_view(), name='detail'),    
    path('checkout/', checkout_home, name='checkout'),
    path('checkout/success/', checkout_done_view, name='success'),
    path('update/', cart_update, name='update'),
]
