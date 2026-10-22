from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.shortcuts import reverse
from tags.models import Tag

User = get_user_model()


class BlogManagerQuerySet(models.query.QuerySet):
    def public_post(self):
        return self.filter(is_public=True)


class BlogManager(models.Manager):
    def get_queryset(self):
        return BlogManagerQuerySet(self.model, using=self._db)

    def public_post(self):
        return self.get_queryset().public_post()


class Blog(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    date = models.DateTimeField(auto_now=False)
    blog_post = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    is_public = models.BooleanField(default=False)
    updated = models.DateTimeField(default=timezone.now)
    meta_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-date',)

    objects = BlogManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})
