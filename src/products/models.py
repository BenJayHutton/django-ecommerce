from django.db import models

class TagQuerySet(models.query.QuerySet):
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

class ProductManager(models.Manager):
    pass

class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.FloatField(default=0.00, max_length=2)
    vat = models.FloatField(default=0.00, max_length=2)
    image = models.ImageField(default='products/150x150.png', upload_to='products/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)
    weight_in_grams = models.FloatField(default=0.00, max_length=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def __str__(self):
        return self.title
