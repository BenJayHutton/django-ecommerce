from django.contrib import admin

from .models import Payment, Card, Charge, PaypalPayment, StripePayment


class PaymentAdmin(admin.ModelAdmin):
    search_fields = ['order', 'user__email', 'paypalOrderID', 'paypalPayerID', 'stripeID']
    list_display = ('paymentMethod', 'order', 'is_paid')

    class Meta:
        model = Payment


class CardAdmin(admin.ModelAdmin):
    search_fields = ['billing_profile__user__email', 'stripe_id']

    class Meta:
        model = Card


class ChargeAdmin(admin.ModelAdmin):
    search_fields = ['billing_profile__user__email', 'stripe_id']

    class Meta:
        model = Charge


class PaypalPaymentAdmin(admin.ModelAdmin):
    search_fields = ['paypalOrderID', 'paypalPayerID', 'brainTreeID']

    class Meta:
        model = PaypalPayment


class StripePaymentAdmin(admin.ModelAdmin):
    search_fields = ['stripe_id']

    class Meta:
        model = StripePayment


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(PaypalPayment, PaypalPaymentAdmin)
admin.site.register(StripePayment, StripePaymentAdmin)
