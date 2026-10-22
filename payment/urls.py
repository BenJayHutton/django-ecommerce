from django.urls import path

from .views import StripeCharge, StripeAdminView, PaypalAdminView
from .services import StripeWebhook

urlpatterns = [
    path('stripe/charge/', StripeCharge.as_view(), name='StripeCharge'),
    path('stripe/webhook/', StripeWebhook.as_view(), name='StripeWebhook'),
    path('stripe/admin/', StripeAdminView.as_view(), name='StripeAdmin'),
    path('paypal/admin/', PaypalAdminView.as_view(), name='PaypalAdmin'),
]
