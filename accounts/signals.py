from django.dispatch import Signal
from django.db.models.signals import pre_save, post_save

from .models import EmailActivation, User

from ecommerce.utils import unique_key_generator

user_logged_in = Signal()

def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)


pre_save.connect(pre_save_email_activation, sender=EmailActivation)


def post_save_email_activation(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(
            user=instance, email=instance.email)
        obj.send_activation_email()


post_save.connect(post_save_email_activation, sender=User)