from django.contrib import admin

from .models import Blog

list_display = ('email','staff' ,'admin', 'is_active')
list_filter = ('admin', 'staff', 'is_active')
search_fields = ('email', 'full_name')
ordering = ('email',)

admin.site.register(Blog)
