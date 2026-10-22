from django.contrib import admin

from .models import BillingProfile


class BillingAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'customer_id']
    list_display = ('customer_id', 'email', 'active')
    ordering = ('customer_id',)
    list_filter = ('active',)
    filter_horizontal = ()

    class Meta:
        model = BillingProfile


admin.site.register(BillingProfile, BillingAdmin)
