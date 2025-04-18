from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from .models import MarketingPreference
from .utils import Mailchimp


@receiver(post_save, sender=MarketingPreference)
def marketing_pref_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        status_code, response_data = Mailchimp().subscribe(instance.user.email)


@receiver(pre_save, sender=MarketingPreference)
def marketing_pref_update_receiver(sender, instance, *args, **kwargs):
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            status_code, response_data = Mailchimp().subscribe(instance.user.email)
        else:
            status_code, response_data = Mailchimp().unsubscribe(instance.user.email)
        
        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
            instance.mailchimp_msg = response_data
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False
            instance.mailchimp_msg = response_data


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def make_marketing_pref_receiver(sender, instance, created, *args, **kwargs):
    # User Model
    if created:
        MarketingPreference.objects.get_or_create(user=instance)
