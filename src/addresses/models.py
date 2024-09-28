from django.db import models

from billing.models import BillingProfile

ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)

LIST_OF_COUNTRIES = (
    ('UK', 'United Kingdom'),
    ('USA', 'United States of America')
)


class Address(models.Model):
    billing_profile = models.ForeignKey(
        BillingProfile, null=True, on_delete=models.SET_NULL)
    label = models.CharField(max_length=255, blank=True, null=True)
    address_type = models.CharField(max_length=12, choices=ADDRESS_TYPE)
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=120)
    country = models.CharField(
        max_length=120,
        choices=LIST_OF_COUNTRIES,
        default='UK')
    meta_data = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.get_address())

    def get_address(self):
        return "{line1}\n{line2}\n{city}\n{state}, {postal}\n{country}".format(
            line1=self.address_line_1,
            line2=self.address_line_2 or "",
            city=self.city,
            state=self.state,
            postal=self.postal_code,
            country=self.country
        )
