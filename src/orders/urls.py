from django.urls import path, re_path
from .views import (
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    OrderUpdateView,
    VerifyOwnership, 
    OrderConfirmation,
    order_delete_view,
)

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('endpoint/verify/ownership/', VerifyOwnership.as_view(), name='verify-ownership'),
    path('confirmation/', OrderConfirmation.as_view(), name='confirmation'),
    path('create/', OrderCreateView.as_view(), name='create'),    
    re_path('update/(?P<pk>[0-9A-Za-z]+)/', OrderUpdateView.as_view(), name='update'),
    re_path('delete/(?P<pk>[0-9A-Za-z]+)/', order_delete_view, name='delete'),
    re_path('(?P<order_id>[0-9A-Za-z]+)', OrderDetailView.as_view(), name='detail'),
]
