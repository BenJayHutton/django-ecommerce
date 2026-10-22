from django.urls import path, re_path


from .views import (
    BookkeepingListView,
    SalesLedgerListView, SalesCreateView, SalesUpdateView, SalesDetailView, SalesDeleteView,
    PurchaseLedgerListView, PurchaseCreateView, PurchaseDeleteView, PurchaseDetailView, PurchaseUpdateView,
    VatLedgerListView, VatCreateView, VatDeleteView, VatDetailView, VatUpdateView,
    CapitalLedgerListView, CapitalCreateView, CapitalDeleteView, CapitalDetailView, CapitalUpdateView,
    CashBookListView, CashbookCreateView, CashbookUpdateView, CashbookDetailView, CashbookDeleteView,
    )

urlpatterns = [
    path('', BookkeepingListView.as_view(), name='home'),
    path('cashbook/', CashBookListView.as_view(), name='cashbook'),
    re_path('cashbook_detail/(?P<pk>[0-9A-Za-z]+)/', CashbookDetailView.as_view(), name='cashbook_detail'),
    path('cashbook_create/', CashbookCreateView.as_view(), name='cashbook_create'),
    path('cashbook/<int:pk>/update/', CashbookUpdateView.as_view(), name='cashbook_update'),
    path('cashbook/<int:pk>/delete/', CashbookDeleteView.as_view(), name='cashbook_delete'),
    
    path('sales_ledger/', SalesLedgerListView.as_view(), name='sales_ledger'),
    re_path('sales_detail/(?P<pk>[0-9A-Za-z]+)/', SalesDetailView.as_view(), name='sales_detail'),
    path('sales_create/', SalesCreateView.as_view(), name='sales_create'),
    path('sales/<int:pk>/update/', SalesUpdateView.as_view(), name='sales_update'),
    path('sales/<int:pk>/delete/', SalesDeleteView.as_view(), name='sales_delete'),

    path('purchase_ledger/', PurchaseLedgerListView.as_view(), name='purchase_ledger'),
    re_path('purchase_detail/(?P<pk>[0-9A-Za-z]+)/', PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchase_create/', PurchaseCreateView.as_view(), name='purchase_create'),    
    path('purchase/<int:pk>/update/', PurchaseUpdateView.as_view(), name='purchase_update'),
    path('purchase/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='purchase_delete'),    
    
    path('vat_ledger/', VatLedgerListView.as_view(), name='vat_ledger'),
    re_path('vat_detail/(?P<pk>[0-9A-Za-z]+)/', VatDetailView.as_view(), name='vat_detail'),
    path('vat_create/', VatCreateView.as_view(), name='vat_create'),
    path('vat/<int:pk>/update/', VatUpdateView.as_view(), name='vat_update'),
    path('vat/<int:pk>/delete/', VatDeleteView.as_view(), name='vat_delete'),    
    
    path('capital_ledger/', CapitalLedgerListView.as_view(), name='capital_ledger'),
    re_path('capital_detail/(?P<pk>[0-9A-Za-z]+)/', CapitalDetailView.as_view(), name='capital_detail'),
    path('capital_create/', CapitalCreateView.as_view(), name='capital_create'),
    path('capital/<int:pk>/update/', CapitalUpdateView.as_view(), name='capital_update'),
    path('capital/<int:pk>/delete/', CapitalDeleteView.as_view(), name='capital_delete'),
]
