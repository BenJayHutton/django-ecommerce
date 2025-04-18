from django.db.models.signals import post_save
from .models import BillingProfile
from django.conf import settings

User = settings.AUTH_USER_MODEL

def user_created_reciever(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(
            user=instance, email=instance.email)


post_save.connect(user_created_reciever, sender=User)