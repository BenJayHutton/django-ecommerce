from django.conf import settings
from django.db import models
from django.urls import reverse

import json

User = settings.AUTH_USER_MODEL

DEBIT_CREDIT = (
    ('DEBIT','Debit'),
    ('CREDIT','Credit'),
)

TRANSACTION_TYPE = (
    ('EXPENSE','Expense'),
    ('ASSET','Asset'),
    ('DRAWING','Drawing'),
    ('LIABILITY','Liability'),
    ('INCOME','Income'),
    ('CAPITAL','Capital'),
    ('SALE','Sale'),
    ('PURCHASE','Purchase'),
)

PAYMENT_PROCESSOR = (
    ('STRIPE', 'Stripe'),
    ('PAYPAL', 'PayPal'),
    ('CASH', 'Cash'),
    ('NO_PAYMENT', 'No payment'),
)


class AbstractAccountingLedger(models.Model):
    user = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    debit_credit = models.CharField(choices=DEBIT_CREDIT, default='DEBIT', max_length=6)
    transaction_date = models.DateTimeField(auto_now=False)
    narrative = models.TextField(default="")
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, default='EXPENSE', max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    ledger_name = "ledger"

    class Meta:
        verbose_name_plural = "Ledgers"
        abstract = True

    def __str__(self):
        return f"{self.narrative}, Transaction type: {self.transaction_type} Amount: £{self.amount}"

    def get_absolute_url(self):
        return reverse(f"bookkeeping:{self.ledger_name}_detail", kwargs={'pk': self.pk})
    
    def get_ledger_url(self):
        return reverse(f"bookkeeping:{self.ledger_name}_ledger")

    def create_ledger_url(self):
        return reverse(f"bookkeeping:{self.ledger_name}_create")

    def delete_ledger_url(self):
        return reverse(f"bookkeeping:{self.ledger_name}_delete", kwargs={'pk': self.pk})
    
    def update_ledger_url(self):
        return reverse(f"bookkeeping:{self.ledger_name}_update", kwargs={'pk': self.pk})

class CashBookManager(models.Manager):
    def new_or_get(self, request):
        return True

    def credit_transactions(self,request):
        if request.user.is_admin:
            return super().get_queryset().filter(debit_credit="credit")
        return None


class CashBook(AbstractAccountingLedger):

    objects = CashBookManager()
    ledger_name = "cashbook"

    class Meta:
        verbose_name_plural = "Cashbook"

    def get_ledger_url(self):
        return reverse(f"bookkeeping:{self.ledger_name}")
    


class SalesLedgerManager(models.Manager):
    def new_or_get(self):
        return True


class SalesLedger(AbstractAccountingLedger):
    
    objects = SalesLedgerManager()
    ledger_name = "sales"

    class Meta:
        verbose_name_plural = "Sales Ledger"


class PurchaseLedgerManager(models.Manager):
    def new_or_get(self):
        return True


class PurchaseLedger(AbstractAccountingLedger):

    objects = PurchaseLedgerManager()
    ledger_name = "purchase"

    class Meta:
        verbose_name_plural = "Purchase Ledger"



class VatLedgerManager(models.Manager):
    def new_or_get(self):
        return True


class VatLedger(AbstractAccountingLedger):

    objects = PurchaseLedgerManager()

    ledger_name = "vat"

    class Meta:
        verbose_name_plural = "VAT Ledger"


class CapitalLedgerManager(models.Manager):
    def new_or_get(self):
        return True


class CapitalLedger(AbstractAccountingLedger):

    objects = CapitalLedgerManager()

    ledger_name = "capital"

    class Meta:
        verbose_name_plural = "Capital Ledger"
