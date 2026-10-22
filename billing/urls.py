from django.urls import path
from .views import pay_method_view, pay_method_createview

urlpatterns = [
    path('payment-method/', pay_method_view, name='billing-payment-method'),
    path('payment-method/create/', pay_method_createview, name='billing-payment-method-endpoint'),
]
