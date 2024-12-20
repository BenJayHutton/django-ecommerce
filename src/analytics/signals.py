from django.core.signals import request_finished
from django.db.models.signals import post_save, pre_save
from django.dispatch import Signal, receiver
from django.contrib.contenttypes.models import ContentType

from .models import ObjectViewed, UserSession
from .utils import get_client_ip

from accounts.signals import user_logged_in

object_viewed_signal = Signal()

def object_viewed_receiver(sender, instance, request, *args, **kwargs):
    c_type = ContentType.objects.get_for_model(
        sender)  # same as instance.__class__
    user = None
    if request.user.is_authenticated:
        user = request.user
    new_view_obj = ObjectViewed.objects.create(
        user=user,
        content_type=c_type,
        object_id=instance.id,
        ip_address=get_client_ip(request),
    )

object_viewed_signal.connect(object_viewed_receiver)


def post_save_session_receiver(sender, instance, created, *args, **kwargs):
    if created:
        qs = UserSession.objects.filter(
            user=instance.user,
            ended=False,
            active=False).exclude(
            id=instance.id)
        for i in qs:
            i.end_session()
    if not instance.active and not instance.ended:
        instance.end_session()

post_save.connect(post_save_session_receiver, sender=UserSession)

#@receiver(request_finished)
def user_logged_in_receiver(sender, instance, request, *args, **kwargs):
    user = instance
    ip_address = get_client_ip(request)
    session_key = request.session.session_key
    UserSession.objects.create(
        user=user,
        ip_address=ip_address,
        session_key=session_key,
    )
user_logged_in.connect(user_logged_in_receiver)