from django.contrib import admin

from .models import Product, Tag

class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'image', 'user', 'public', 'quantity']

    class Meta:
        model = Product

admin.site.register(Product,ProductAdmin,)
admin.site.register(Tag)
