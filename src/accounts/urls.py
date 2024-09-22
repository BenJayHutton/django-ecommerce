from django.urls import path, re_path

from .views import Accounts

app_name = 'accounts'

urlpatterns = [
    path('', Accounts.as_view(), name='home'),
]