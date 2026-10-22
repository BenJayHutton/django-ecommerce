from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    DeleteView,
)

from .forms import CashbookForm, CapitalLedgerForm, PurchaseLedgerForm, SalesLedgerForm, VatLedgerForm

from .models import CashBook, SalesLedger, PurchaseLedger, VatLedger, CapitalLedger

class LedgerListView(LoginRequiredMixin, ListView):
    template_name = 'bookkeeping/ledger.html'
    ledger_title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["credit_transactions"] = self.object_list.filter(
            debit_credit="Credit"
        )
        context["debit_transactions"] = self.object_list.filter(
            debit_credit="Debit"
        )
        context["ledger_title"] = self.ledger_title
        context["create_ledger_url"] = self.model().create_ledger_url()
        return context


class LedgerDetailView(LoginRequiredMixin, DetailView):
    def get(self, *args, **kwargs):
        if not self.request.user.staff:
            return redirect("home")
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form) 


class LedgerCreateView(LoginRequiredMixin, CreateView):
    form_class = CashbookForm
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class LedgerUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'bookkeeping/ledger_create.html'

    def get(self, *args, **kwargs):
        if not self.request.user.staff:
            return redirect("bookkeeping:home")
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)


class LedgerDeleteView(LoginRequiredMixin, DeleteView):
    model = None
    ledger_name = "ledger"
    success_url = None
    template_name = 'bookkeeping/ledger_delete.html'


class BookkeepingListView(ListView):
    template_name = 'bookkeeping/home.html'

    def get_queryset(self):
        return True


class CashBookListView(LedgerListView):
    model = CashBook
    ledger_title = "Cashbook"


class CashbookCreateView(CreateView):
    template_name = 'bookkeeping/ledger_create.html'
    form_class = CashbookForm
    queryset = CashBook.objects.all()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CashbookUpdateView(LedgerUpdateView):
    model = CashBook
    queryset = model.objects.all()
    form_class = CashbookForm


class CashbookDeleteView(LedgerDeleteView):
    model = CashBook
    ledger_name = "cashbook"
    success_url = reverse_lazy("bookkeeping:cashbook")


class CashbookDetailView(LedgerDetailView):
    template_name = 'bookkeeping/ledger_detail.html'
    form_class = CashbookForm
    queryset = CashBook.objects.all()


class SalesLedgerListView(LedgerListView):
    model = SalesLedger
    ledger_title = "sales"


class SalesDetailView(LedgerDetailView):
    template_name = 'bookkeeping/ledger_detail.html'
    form_class = SalesLedgerForm
    queryset = SalesLedger.objects.all()


class SalesCreateView(LedgerCreateView):
    template_name = 'bookkeeping/ledger_create.html'
    form_class = SalesLedgerForm
    queryset = SalesLedger.objects.all()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SalesUpdateView(LedgerUpdateView):
    model = SalesLedger
    form_class = SalesLedgerForm
    queryset = model.objects.all()


class SalesDeleteView(LedgerDeleteView):
    model = SalesLedger
    ledger_name = "sales"
    success_url = reverse_lazy("bookkeeping:sales_ledger")


class PurchaseLedgerListView(LedgerListView):
    model = PurchaseLedger
    ledger_title = "purchase"


class PurchaseDetailView(LedgerDetailView):
    template_name = 'bookkeeping/ledger_detail.html'
    form_class = PurchaseLedgerForm
    queryset = PurchaseLedger.objects.all()


class PurchaseCreateView(CreateView):
    template_name = 'bookkeeping/ledger_create.html'
    form_class = PurchaseLedgerForm
    queryset = PurchaseLedger.objects.all()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PurchaseUpdateView(LedgerUpdateView):
    model = PurchaseLedger
    form_class = PurchaseLedgerForm
    queryset = model.objects.all()


class PurchaseDeleteView(LedgerDeleteView):
    model = PurchaseLedger
    ledger_name = "purchase"
    success_url = reverse_lazy("bookkeeping:purchase_ledger")


class VatLedgerListView(LedgerListView):
    model = VatLedger
    ledger_title = "vat"


class VatDetailView(LedgerDetailView):
    template_name = 'bookkeeping/ledger_detail.html'
    form_class = VatLedgerForm
    queryset = VatLedger.objects.all()


class VatCreateView(LedgerCreateView):
    template_name = 'bookkeeping/ledger_create.html'
    form_class = VatLedgerForm
    queryset = VatLedger.objects.all()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class VatUpdateView(LedgerUpdateView):
    model = VatLedger
    form_class = VatLedgerForm
    queryset = model.objects.all()


class VatDeleteView(LedgerDeleteView):
    model = VatLedger
    ledger_name = "vat"
    success_url = reverse_lazy("bookkeeping:vat_ledger")


class CapitalLedgerListView(LedgerListView):
    model = CapitalLedger
    ledger_title = "capital"


class CapitalDetailView(LedgerDetailView):
    template_name = 'bookkeeping/ledger_detail.html'
    form_class = CapitalLedgerForm
    queryset = CapitalLedger.objects.all()


class CapitalCreateView(LedgerCreateView):
    template_name = 'bookkeeping/ledger_create.html'
    form_class = CapitalLedgerForm
    queryset = CapitalLedger.objects.all()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CapitalUpdateView(LedgerUpdateView):
    model = CapitalLedger
    form_class = CapitalLedgerForm
    queryset = model.objects.all()


class CapitalDeleteView(LedgerDeleteView):
    model = CapitalLedger
    ledger_name = "capital"
    success_url = reverse_lazy("bookkeeping:capital_ledger")
