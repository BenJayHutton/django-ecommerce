from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from .views import about_page, contact_page, DefaultHomePage
from addresses.views import (
     checkout_address_create_view,
     checkout_address_reuse_view,
     checkout_address_change_view
     )
from orders.views import LibraryView


urlpatterns = [
    path('', DefaultHomePage.as_view(display_name="home"), name='home'),
    path('about/', about_page, name='about'),
    path('admin/', admin.site.urls),
    path('account/', include(("accounts.urls", "accounts"), namespace='account')),
    path('accounts/', include(("accounts.urls", "accounts"), namespace='accounts')),
    path('accounts/', include("accounts.password.urls")),
    path('address/', include("addresses.urls", namespace='address')),
    path('analytics/', include(("analytics.urls", "analytics"), namespace='analytics')),
    path('billing/', include(("billing.urls", "billing"), namespace='billing')),
    path('blog/', include(("blog.urls", "blog"), namespace='blog')),
    path('bookkeeping/', include(("bookkeeping.urls", "bookkeeping"), namespace='bookkeeping')),
    path('cart/', include(("carts.urls", "carts"), namespace='cart')),
    path('carts/', include(("carts.urls", "carts"), namespace='carts')),
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('checkout/address/change/', checkout_address_change_view, name='checkout_address_change'),
    path('contact/', contact_page, name='contact'),
    path('library/', LibraryView.as_view(), name='library'),
    path('marketing/', include(("marketing.urls", "marketing"), namespace='marketing')),
    path('orders/', include(("orders.urls", "orders"), namespace='orders')),
    path('products/', include(("products.urls", "products"), namespace='products')),
    path('payment/', include(("payment.urls", "payment"), namespace='payment')),
    path('search/', include(("search.urls", "search"), namespace='search')),
    path('currier/', include(("currier.urls", "currier"), namespace='currier')),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
     from django.conf.urls.static import static
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)