from django.urls import path

from .views import (
    BillingProfileView,
    CartView,
    SalesView,
    SalesAjaxView,
    OrderView,
    ObjectViewList,
    ProductView,
)

urlpatterns = [
    path('orders/', CartView.as_view(), name='carts'),
    path('orders/', OrderView.as_view(), name='orders'),
    path('billing-profiles/', BillingProfileView.as_view(), name='billing-profiles'),
    path('products/', ProductView.as_view(), name='products'),
    path('sales/', SalesView.as_view(), name='sales-analytics'),
    path('sales/data/', SalesAjaxView.as_view(), name='sales-data'),
    path('data/', ObjectViewList.as_view(), name='analytics-data'),
]
