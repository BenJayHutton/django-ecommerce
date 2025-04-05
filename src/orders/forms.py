from django import forms
import datetime

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        now = datetime.datetime.now().date()
        model = Order
        fields = [
            'billing_profile',
            'order_id',
            'shipping_address',
            'cart',
            'status',
            'shipping_total',
            'tax',
            'total',
            'active',
            'meta_data'
            ]
        widgets = {}


