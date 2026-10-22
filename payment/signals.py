from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Card

@receiver(post_save, sender=Card)
def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(
            billing_profile=billing_profile).exclude(
            pk=instance.pk)
        qs.update(default=False)
