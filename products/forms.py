from django import forms
import datetime

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        now = datetime.datetime.now().date()
        model = Product
        fields = ['title', 'description', 'price', 'price', 'image', 'featured', 'quantity', 'weight_in_grams', 'tags', 'active', 'is_digital']
        widgets = {
            "date": forms.SelectDateWidget(
                years=range(2015,2040),
                attrs={
                    "value": now
                }
            ),
        }
