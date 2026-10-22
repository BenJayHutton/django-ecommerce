from django.contrib import admin

from .models import Currier

admin.site.register(Currier)

class CurrierAdmin(admin.StackedInline):
    model = Currier
    ordering = ('-pk')