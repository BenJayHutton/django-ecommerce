from django.conf import settings
from django.db import models
from django.utils import timezone


class MarketingPreference(models.Model):
    user                    = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    subscribed              = models.BooleanField(default=True)
    mailchimp_subscribed    = models.BooleanField(null=True)
    mailchimp_msg           = models.TextField(null=True, blank=True)
    meta_data               = models.TextField(null=True, blank=True)
    timestamp               = models.DateTimeField(default=timezone.now)
    updated                 = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.email
