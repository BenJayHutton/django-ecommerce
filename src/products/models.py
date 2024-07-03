from django.conf import settings
from django.db import models
from django.db.models import Q

User = settings.AUTH_USER_MODEL

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
    
class ProductQuerySet(models.query.QuerySet):  # class.objects.all().attribute
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)
    
    def get_product_by_id(self, id):
        return self.filter(id=id)

    def search(self, query):
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(price__icontains=query)|
                   Q(tags__name__icontains=query)
                   )
        return self.filter(lookups)


class ProductManager(models.Manager):
    # overriding get_queryset so we can use the queryset above
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def featured(self):
        return self.get_queryset().featured()
    
    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        else:
            return None
        
    def search(self, query):
        return self.get_queryset().active().search(query)

class Product(models.Model):
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField(blank=True, null=True)
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

    def get_discount(self):
        return "122"