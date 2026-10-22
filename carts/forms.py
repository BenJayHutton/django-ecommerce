from django import forms
import datetime

from .models import Cart, CartItem


class CartForm(forms.ModelForm):
    class Meta:
        now = datetime.datetime.now().date()
        model = Cart
        fields = ['user', 'cart_items', 'vat', 'subtotal', 'meta_data','weight_in_grams']
        widgets = {
        }

class CartItemForm(forms.ModelForm):
    class Meta:
        now = datetime.datetime.now().date()
        model = Cart
        fields = []
        widgets = {
        }
