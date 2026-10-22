from django.shortcuts import render
from django.views.generic import View

# Create your views here.

class Shipping():
    api_key=None
    base_url=None
    
    def collect(self):
        context= {
            'collect':float(0.00)
        }
        return context



class Dhl(Shipping):
    base_url="Dhl"


class CollectPus(Shipping):
    base_url="CollectPus"


class FedEx(Shipping):
    base_url="FedEx"


class RoyalMail(Shipping):
    def get_shipping_cost(self, weight=None):
        first_class = self.first_class(weight)
        return first_class
        

    def first_class(weight=None):
        cost=float(0.00)
        if weight is not None:
            if weight >0 and weight <=100:
                cost = 0.95
            elif weight >= 100 and weight <= 249:
                cost = 1.65
            elif weight >= 250 and weight <= 499:
                cost = 2.15
            elif weight >= 500 and weight <= 749:
                cost = 2.70
            elif weight >= 750 and weight <=1999:
                cost = 2.85
            elif weight > 2000 and weight <=4999:
                cost = 5.95
            elif weight >= 5000 and weight <=9999:
                cost = 6.95
            elif weight >= 10000 and weight <=14999:
                cost = 11.95
            elif weight >= 15000 and weight <=20000:
                cost = 11.95
            else:
                cost = 0.00
        return cost

    def second_class(weight=None):
        pass
