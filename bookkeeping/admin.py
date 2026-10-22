from django.contrib import admin

from .models import CashBook, SalesLedger, PurchaseLedger, VatLedger, CapitalLedger

class CashBookAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'narrative', 'amount']
    list_display = ('transaction_date', 'transaction_type', 'narrative', 'amount')

    class Meta:
        model = CashBook


class SalesLedgerAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'narrative', 'amount']
    list_display = ('transaction_date', 'transaction_type', 'narrative', 'amount')

    class Meta:
        model = SalesLedger


class PurchaseLedgerAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'narrative', 'amount']
    list_display = ('transaction_date', 'transaction_type', 'narrative', 'amount')

    class Meta:
        model = PurchaseLedger


class VatLedgerAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'narrative', 'amount']
    list_display = ('transaction_date', 'transaction_type', 'narrative', 'amount')

    class Meta:
        model = VatLedger


class CapitalLedgerAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'narrative', 'amount']
    list_display = ('transaction_date', 'transaction_type', 'narrative', 'amount')

    class Meta:
        model = CapitalLedger


admin.site.register(CashBook, CashBookAdmin)
admin.site.register(SalesLedger, SalesLedgerAdmin)
admin.site.register(PurchaseLedger, PurchaseLedgerAdmin)
admin.site.register(VatLedger, VatLedgerAdmin)
admin.site.register(CapitalLedger, CapitalLedgerAdmin)