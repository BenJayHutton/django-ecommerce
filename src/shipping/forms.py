from django import forms
import datetime

from .models import Shipping


class ShippingForm(forms.ModelForm):
    class Meta:
        now = datetime.datetime.now().date()
        model = Shipping
        fields = []
        widgets = {
        }