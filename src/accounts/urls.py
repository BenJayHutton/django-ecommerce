from django.urls import path, re_path

from products.views import UserProductHistoryView

from .views import (
    Accounts,
    LoginView,
    RegisterView,
    logout_view,
    GuestRegisterView,
    AccountEmailActivateView,
    UserDetailUpdateView,
)

app_name = 'accounts'

urlpatterns = [
    path('', Accounts.as_view(), name='home'),
    path('details/', UserDetailUpdateView.as_view(), name='user-update'),
    path('history/products/', UserProductHistoryView.as_view(), name='user-product-history'),
    re_path('email/confirm/(?P<key>[0-9A-Za-z]+)/', AccountEmailActivateView.as_view(), name='email-activate'),
    path('email/resend-activation/', AccountEmailActivateView.as_view(), name='resend-activation'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/guest/', GuestRegisterView.as_view(), name='guest_register'),
    path('logout/', logout_view, name='logout'),
]
