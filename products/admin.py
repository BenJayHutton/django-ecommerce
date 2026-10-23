from django.contrib import admin

from .models import Category, Product, ItemImage, ProductFile

class ProductFileInline(admin.TabularInline):
    model = ProductFile
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    class Meta:
        model = Category


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'image']
    inlines = [ProductFileInline]

    class Meta:
        model = Product


admin.site.register(Category,CategoryAdmin,)
admin.site.register(Product,ProductAdmin,)
admin.site.register(ItemImage)
