from django.contrib import admin

from .models import BillingProfile


class BillingAdmin(admin.ModelAdmin):
    list_display = ('user','email', 'session_key')
    search_fields = ['user', 'email']
    ordering = ('user', 'email', 'session_key')

    class Meta:
        model = BillingProfile


admin.site.register(BillingProfile, BillingAdmin)
