from django.db.models.signals import pre_save
from django.dispatch import receiver
from eCommerce.utils import unique_slug_generator
from .models import Blog


@receiver(pre_save, sender=Blog)
def blog_pre_save_receiver(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)