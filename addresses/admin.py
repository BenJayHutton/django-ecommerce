from django.contrib import admin

from .models import Address

class AddressAdmin(admin.ModelAdmin):
    search_fields = ['billing_profile', 'user']
    list_display = ('billing_profile','label', 'address_line_1', 'postal_code', 'address_type', 'session_key')
    list_filter = ('billing_profile', 'user')

    class Meta:
        model = Address

admin.site.register(Address, AddressAdmin)