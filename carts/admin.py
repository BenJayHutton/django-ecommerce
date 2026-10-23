from django.contrib import admin

from .models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    search_fields = ['session_key', 'user__email']
    list_display = ('user__email', 'session_key', 'total', 'is_active')
    list_filter = ('is_active',)
    ordering = ('-timestamp',)


    class Meta:
        model = Cart


class CartItemAdmin(admin.ModelAdmin):
    search_fields = ['session_key', 'product__title']
    list_display = ('session_key', 'product__title', 'quantity', 'is_active')
    list_filter = ('is_active',)
    ordering = ('-timestamp',)


    class Meta:
        model = CartItem

admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Cart, CartAdmin)
