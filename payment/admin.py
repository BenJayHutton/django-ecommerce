from django.contrib import admin

from .models import (
    PaypalPayment,
    Stripe,
    StripeCheckoutSession,
    StripePaymentIntent,
    StripeCharge,
    StripeProduct,
    StripePrice,
    StripeCustomer
    )


class PaypalPaymentAdmin(admin.ModelAdmin):
    search_fields = ['paypalOrderID', 'paypalPayerID', 'brainTreeID']

    class Meta:
        model = PaypalPayment


class StripeAdmin(admin.ModelAdmin):
    search_fields = ['user', 'order', 'checkout_session', 'customer']

    class Meta:
        model = Stripe


class StripeChargeAdmin(admin.ModelAdmin):
    list_display = ('customer_email', 'charge_id', 'payment_intent_id', 'created_at')
    ordering = ('customer_email', 'charge_id', 'payment_intent_id', 'created_at')
    search_fields = ['charge_id', 'payment_intent_id', 'customer_email', 'metadata']

    class Meta:
        model = StripeCharge


class StripeCheckoutSessionAdmin(admin.ModelAdmin):
    search_fields = ['event_id']

    class Meta:
        model = StripeCheckoutSession


class StripePaymentIntentAdmin(admin.ModelAdmin):
    search_fields = ['payment_intent_id']

    class Meta:
        model = StripePaymentIntent

class StripeProductAdmin(admin.ModelAdmin):
    search_fields = ['payment_intent_id']

    class Meta:
        model = StripeProduct


class StripePriceAdmin(admin.ModelAdmin):
    search_fields = ['payment_intent_id']

    class Meta:
        model = StripePrice


class StripeCustomerAdmin(admin.ModelAdmin):
    search_fields = ['payment_intent_id']

    class Meta:
        model = StripeCustomer

admin.site.register(PaypalPayment, PaypalPaymentAdmin)
admin.site.register(Stripe, StripeAdmin)
admin.site.register(StripeCharge, StripeChargeAdmin)
admin.site.register(StripeCheckoutSession, StripeCheckoutSessionAdmin)
admin.site.register(StripePaymentIntent, StripePaymentIntentAdmin)
admin.site.register(StripeProduct, StripeProductAdmin)
admin.site.register(StripePrice, StripePriceAdmin)
admin.site.register(StripeCustomer, StripeCustomerAdmin)