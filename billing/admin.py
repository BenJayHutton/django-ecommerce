from django.contrib import admin

from .models import BillingProfile


class BillingAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'session_key']
    list_display = ('email', 'session_key', 'active')
    ordering = ('email',)
    list_filter = ('active',)
    filter_horizontal = ()

    class Meta:
        model = BillingProfile


admin.site.register(BillingProfile, BillingAdmin)
