from django.contrib import admin

from .models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "public"]
    ordering = ["name"]

    class Meta:
        model = Tag

admin.site.register(Tag, TagAdmin)
