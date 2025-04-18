from django.dispatch import Signal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import EmailActivation, User

user_logged_in = Signal()
from eCommerce.utils import unique_key_generator


@receiver(pre_save, sender=EmailActivation)
def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)


@receiver(post_save, sender=User)
def post_save_email_activation(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(
            user=instance, email=instance.email)
        obj.send_activation_email()
