from django.conf import settings
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse

from tags.models import Tag

User = settings.AUTH_USER_MODEL
    
class ProductQuerySet(models.query.QuerySet):  # class.objects.all().attribute
    def is_active(self):
        return self.filter(active=True)

    def is_featured(self):
        return self.filter(featured=True, active=True)
    
    def is_public(self):
        return self.filter(public=True, active=True)
    
    def get_product_by_id(self, id):
        return self.filter(id=id)

    def search(self, query, user=None):
        lookup = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(price__icontains=query)|
                   Q(tags__name__icontains=query)
                   )
        qs = self.is_public().filter(lookup)
        if user is not None:
            qs2 = self.filter(user=user).filter(lookup)
            qs = (qs|qs2).distinct()
        return qs


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
        
    def search(self, query, user=None):
        return self.get_queryset().search(query, user=user)



class Product(models.Model):
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(default='products/150x150.png', upload_to='products/', null=True, blank=True)
    price = models.FloatField(default=0.00, max_length=2)
    vat = models.FloatField(default=0.00, max_length=2)
    quantity = models.IntegerField(default=0)
    weight_in_grams = models.FloatField(default=0.00, max_length=2)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse("product:detail", kwargs={"slug": self.slug})

    @property
    def endpoint(self):
        return self.get_absolute_url()
    
    @property
    def path(self):
        return f"/product/{self.pk}/"
    
    @property
    def body(self):
        return self.description

    def __str__(self):
        return self.title

    def discount(self, discount=0):
        return self.price * discount
    
    def is_public(self):
        return self.public

    def tag_name(self):
        return[str(tags) for tags in self.tags.all()]
