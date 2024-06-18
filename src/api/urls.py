from django.urls import path

from .views import api_home

app_name = 'api'

urlpatterns = [
    path('', api_home)
]