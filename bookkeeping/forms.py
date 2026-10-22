from django import forms
import datetime

from .models import CashBook, SalesLedger,PurchaseLedger,VatLedger, CapitalLedger

class LedgerForm(forms.ModelForm):
    transaction_date = forms.DateField(initial=datetime.date.today)
    class Meta:
        model = None
        fields = ['user','transaction_date', 'debit_credit', 'narrative', 'amount']
        widgets = {
            "transaction_date": forms.SelectDateWidget(
                years=range(2020, 2030),
            )
        }


class CashbookForm(LedgerForm):
    class Meta(LedgerForm.Meta):
        model = CashBook


class SalesLedgerForm(LedgerForm):
    class Meta(LedgerForm.Meta):
        model = SalesLedger


class PurchaseLedgerForm(LedgerForm):
    class Meta(LedgerForm.Meta):
        model = PurchaseLedger


class VatLedgerForm(LedgerForm):
    class Meta(LedgerForm.Meta):
        model = VatLedger


class CapitalLedgerForm(LedgerForm):
    class Meta(LedgerForm.Meta):
        model = CapitalLedger
