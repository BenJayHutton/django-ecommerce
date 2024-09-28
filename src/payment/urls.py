from django.urls import path

from .views import BrainTree, Paypal, Stripe,StripeCharge, StripeWebHook

app_name = 'payment'
urlpatterns = [
    path('brain_tree/', BrainTree.as_view(), name='BrainTree'),
    path('paypal/', Paypal.as_view(), name='paypal'),
    path('stripe/', Stripe.as_view(), name='Stripe'),
    path('stripe/charge/<int:pk>/<order_id>/<str:customer_email>', StripeCharge.as_view(), name='StripeCharge'),
    path('stripe/webhook/', StripeWebHook.as_view(), name='StripeWebhook')
]
