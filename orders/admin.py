from django.contrib import admin

from .models import Order, ProductPurchase


class OrderAdmin(admin.ModelAdmin):
    search_fields = ['order_id', 'billing_profile__email']
    list_display = ('order_id', 'billing_profile', 'timestamp', 'status')
    list_filter = ('active', 'status')
    ordering = ('order_id','billing_profile','timestamp',)


    class Meta:
        model = Order


admin.site.register(Order, OrderAdmin)
admin.site.register(ProductPurchase)
