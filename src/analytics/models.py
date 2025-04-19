from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session

User = settings.AUTH_USER_MODEL

class ObjectViewedQuerySet(models.query.QuerySet):
    def by_model(self, model_class, model_queryset=False):
        c_type = ContentType.objects.get_for_model(model_class)
        qs = self.filter(content_type=c_type)
        if model_queryset:
            viewed_ids = [x.object_id for x in qs]
            return model_class.objects.filter(pk__in=viewed_ids)
        return qs


class ObjectViewedManager(models.Manager):
    def get_queryset(self):
        return ObjectViewedQuerySet(self.model, using=self._db)

    def by_model(self, model_class, model_queryset=False):
        return self.get_queryset().by_model(model_class, model_queryset=model_queryset)


class ObjectViewed(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    ip_address = models.CharField(max_length=220, blank=True, null=True)
    # any sort of object, User, Product, Order, Cart, Address etc
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField()  # id of the object above
    content_object = GenericForeignKey(
        'content_type', 'object_id')  # instance of the object above
    meta_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    objects = ObjectViewedManager()

    def __str__(self):
        return"%s viewed %s" % (self.content_object, self.timestamp)

    class Meta:
        ordering = ['-timestamp']  # ascending order
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'


class UserSession(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    ip_address = models.CharField(max_length=220, blank=True, null=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)
    ended = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    def end_session(self):
        session_key = self.session_key
        ended = self.ended
        try:
            Session.objects.get(pk=session_key).delete()
            self.ended = True
            self.active = False
            self.save()
        except BaseException:
            pass
        return self.ended
