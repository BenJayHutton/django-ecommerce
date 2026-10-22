from django.conf import settings
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.utils import timezone
from decimal import Decimal

from ecommerce.aws.download.utils import AWSDownload
from ecommerce.aws.utils import ProtectedS3Storage
from ecommerce.utils import unique_slug_generator, get_filename
from tags.models import Tag

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(default="General", max_length=120)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class ProductQuerySet(models.query.QuerySet):  # class.objects.all().attribute
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(price__icontains=query)
                   )
        return self.filter(lookups)
    
    def search_tag(self, query):
        lookups = (Q(tags__name__icontains=query))
        return self.filter(lookups)


class ProductManager(models.Manager):
    # overriding get_queryset so we can use the queryset above
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def featured(self):
        return self.get_queryset().featured()
    
    def active(self):
        return self.get_queryset().active()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        else:
            return None

    def search(self, query):
        return self.get_queryset().active().search(query)
    
    def search_tag(self, query):
        return self.get_queryset().active().search_tag(query)

    def increase_qty_of_product(self, *args, **kwargs):
        id = kwargs.get('id')
        quantity = kwargs.get('quantity')
        if id is not None:
            product = self.get_queryset().filter(id=id)
            if product.exists() and quantity is not None:
                product.quantity = product.quantity + quantity
                product.save()
                return True
        else:
            return False

    def decrease_qty_of_product(self, *args, **kwargs):
        id = kwargs.get('id')
        quantity = kwargs.get('quantity')
        if id is not None:
            product = self.get_queryset().filter(id=id)
            if product.exists() and quantity is not None:
                product.quantity = product.quantity - quantity
                product.save()
                return True
        else:
            return False


class Product(models.Model):
    STANDARD_RATE = Decimal('0.20')
    REDUCED_RATE = Decimal('0.05')
    ZERO_RATE = Decimal('0.00')

    VAT_RATE = [
        (STANDARD_RATE,"Standard Rate 20%"),
        (REDUCED_RATE,"Reduced Rate 5%"),
        (ZERO_RATE,"Zero Rate 0%")
    ]
    
    user = models.ForeignKey(User, default=None, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    category = models.ForeignKey(Category,default=None, blank=True, null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    description = models.TextField(default="", blank=True, null=True)
    image = models.ImageField(default='products/150x150.png', upload_to='products/', null=True, blank=True)
    price = models.DecimalField(default=0, max_digits=12, decimal_places=4)
    vat_rate = models.DecimalField(default=0, max_digits=12, decimal_places=4, choices=VAT_RATE)
    quantity = models.IntegerField(default=0)
    weight_in_grams = models.FloatField(default=0, max_length=2)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    objects = ProductManager()

    class Meta:
        ordering = ["tags__name", "title"]
        verbose_name_plural = "products"

    def has_quantity(self):
        return self.quantity > 0

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    def get_by_id(self, id):
        qs = Product.objects.get(pk=id)
        return qs

    def decrease_qty_of_product(self, quantity):
        old_quantity = self.quantity
        self.quantity -= quantity
        self.save()
        new_quantity = self.quantity
        return old_quantity, new_quantity
    
    def price_in_pennies(self):
        return "{:n}".format(int(round(self.price,2) * 100))

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title

    def get_downloads(self):
        qs = self.productfile_set.all()
        return qs


def upload_product_file_loc(instance, filename):
    slug = instance.product.slug
    id_ = instance.id
    if id_ is None:
        Klass = instance.__class__
        qs = Klass.objects.all().order_by('-pk')
        if qs.exists():
            id_ = qs.first().id + 1
        else:
            id_ = 0
    if not slug:
        slug = unique_slug_generator(instance.product)
    location = "product/{slug}/{id}/".format(slug=slug, id=id_)
    return location + filename


class ProductFile(models.Model):
    product = models.ForeignKey(
        Product,
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    name = models.CharField(max_length=120, null=True, blank=True)
    file = models.FileField(
        upload_to=upload_product_file_loc,
        storage=ProtectedS3Storage())
    free = models.BooleanField(default=False)
    user_required = models.BooleanField(default=False)

    def __str__(self):
        return str(self.file.name)

    @property
    def display_name(self):
        og_name = get_filename(self.file.name)
        if self.name:
            return self.name
        return og_name

    def get_default_url(self):
        return self.product.get_absolute_url()

    def generate_download_url(self):
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'S3DIRECT_REGION')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        if not secret_key or not access_key or not bucket or not region:
            return "/product-not-found/"
        PROTECTED_DIR_NAME = getattr(
            settings, 'PROTECTED_DIR_NAME', 'protected')
        path = "{base}/{file_path}".format(base=PROTECTED_DIR_NAME,
                                           file_path=str(self.file))
        aws_dl_object = AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(
            path, new_filename=self.display_name)
        return file_url

    def get_download_url(self):
        return reverse(
            "products:download",
            kwargs={
                "slug": self.product.slug,
                "pk": self.pk})


class ItemImage(models.Model):
    upload_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='item-images/')
    items = models.ManyToManyField(Product)

    def __str__(self):
        return str(self.upload_date)
