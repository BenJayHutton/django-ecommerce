from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class ShippingQuerySet(models.query.QuerySet):
    pass


class ShippingItemManager(models.Manager):
    pass


class Shipping(models.Model):
    pass



"""
user object
cart object,
order obj
currier,
price,
tracking code,
weight,
meta date,

"""