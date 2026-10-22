from django import forms
import datetime

from .models import Currier


class CurrierForm(forms.ModelForm):
    class Meta:
        model = Currier
        fields = ["currier","price"]
        readonly_fields = ["price"]
        widgets = {
        }