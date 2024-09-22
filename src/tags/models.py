from django.db import models


class TagQuerySet(models.query.QuerySet): # class.objects.all().attribute
    def public(self):
        return self.filter(public=True)
    
    def private(self):
        return self.filter(public=False)


class TagManager(models.Manager):
    def get_queryset(self):
        return TagQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_queryset().public()


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    public = models.BooleanField(default=False)
    blurb = models.CharField(max_length=500, null=True)

    objects = TagManager()

    def __str__(self):
        return self.name
