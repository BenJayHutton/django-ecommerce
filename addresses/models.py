from django.conf import settings
from django.db import models
from django.shortcuts import reverse

from billing.models import BillingProfile

User = settings.AUTH_USER_MODEL

ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)

LIST_OF_COUNTRIES = (
    ('UK', 'United Kingdom'),
    ('USA', 'United States of America')
)

class AddressManager(models.Manager):
    def new_or_get(self,request, billing_profile, form):
        session_key = request.session.session_key
        if request.user.is_authenticated:
            qs = self.get_queryset().filter(billing_profile=billing_profile, session_key=session_key).first()
            if qs:
                return qs
            
        if form.is_valid():
            instance = form.save(commit=False)
            if billing_profile:
                instance.billing_profile = billing_profile
            if session_key:
                instance.session_key = session_key
            instance.save()
            return instance
        return None

class Address(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, default=None, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    address_type = models.CharField(max_length=12, choices=ADDRESS_TYPE)
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=120)
    country = models.CharField(max_length=120, choices=LIST_OF_COUNTRIES, default='UK')
    meta_data = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.get_address())
    
    objects = AddressManager()

    def get_address(self):
        return "{line1}\n{line2}\n{city}\n{state}, {postal}\n{country}".format(
            line1=self.address_line_1,
            line2=self.address_line_2 or "",
            city=self.city,
            state=self.state,
            postal=self.postal_code,
            country=self.country
        )
    def get_absolute_url(self):
        return reverse("address:home")
