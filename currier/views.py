from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.urls import reverse_lazy
from decimal import Decimal
from .models import Currier
from .forms import CurrierForm


class Currier(ListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_value'] = 'Hello, World!'
        return context

    def get_curriers_price_list(*args, **kwargs):
        weight = kwargs.get("weight")
        royal_mail_1st = RoyalMail.first_class(weight=weight)
        royal_mail_2nd = RoyalMail.second_class(weight=weight)
        international = FedEx.international(weight=weight)
        couriers = {
            'Royal Mail 1st Class':royal_mail_1st,
            'Royal Mail 2nd class':royal_mail_2nd, 
            'International':international,
            }
        return couriers

    def get_price(*args, **kwargs):
        weight = kwargs.get("weight")
        royal_mail_2nd = RoyalMail.second_class(weight=weight)
        return royal_mail_2nd

class CurrierDetailView(DetailView):
    pass

class CurrierCreateView(CreateView):
    model = Currier
    fields = ["currier", "weight", "price","tracking_code"]
    template_name = 'currier/Currier_form.html'
    success_url = reverse_lazy('checkout:home')
    
    def get(self, request, *args, **kwargs):
        return redirect("cart:checkout")
    
    def post(self, request, *args, **kwargs):
        return redirect("cart:checkout")


class CurrierUpdateView(UpdateView):
    pass

class CurrierDeleteView(DeleteView):
    pass

class Dhl(View):
    base_url="Dhl"


class CollectPus(View):
    base_url="CollectPus"


class FedEx(View):
    base_url="FedEx"
    def international(weight=None):
        return Decimal(7.40)


class RoyalMail(View):
    def get_shipping_cost(weight=None):
        return  Decimal(RoyalMail.second_class(weight=weight))

    def first_class(weight=None):
        cost=float(0.00)
        if weight is not None:
            if weight ==00:
                cost= 0.00
            elif weight >0 and weight <=100:
                cost = 1.80
            elif weight >= 100 and weight <= 249:
                cost = 2.20
            elif weight >= 250 and weight <= 499:
                cost = 2.50
            elif weight >= 500 and weight <= 749:
                cost = 2.75
            elif weight >= 750 and weight <=1999:
                cost = 5.25
            elif weight > 2000 and weight <=4999:
                cost = 11.95
        return Decimal(cost)

    def second_class(weight=None):
        cost=Decimal(0.00)
        if weight is not None:
            if weight == 0:
                cost = 0.0
            if weight >0 and weight <=100:
                cost = 1.0
            elif weight >= 100 and weight <= 249:
                cost = 2.0
            elif weight >= 250 and weight <= 499:
                cost = 3.0
            elif weight >= 500 and weight <= 749:
                cost = 4.0
            elif weight >= 750 and weight <=1999:
                cost = 5.0
            elif weight > 2000 and weight <=4999:
                cost = 6.0
            elif weight >= 5000 and weight <=9999:
                cost = 7.0
            elif weight >= 10000 and weight <=14999:
                cost = 8.0
            elif weight >= 15000:
                cost = 9.0
        return Decimal(cost)
