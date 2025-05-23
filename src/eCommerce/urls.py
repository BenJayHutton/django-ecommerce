"""
URL configuration for eCommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path

from .views import about_page, contact_page, DefaultHomePage

from addresses import views #checkout_address_create_view, checkout_address_reuse_view
from orders.views import LibraryView

app_name = 'eCommerce'

urlpatterns = [
    path('', DefaultHomePage.as_view(), name='home'),
    path('about/', about_page, name='about'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts'), name='accounts'),
    path('accounts/', include("accounts.password.urls")),
    path('analytics/', include(("analytics.urls", "analytics"), namespace='analytics')),
    path('api/', include('api.urls', namespace='api')),
    path('api/v2/', include('eCommerce.routers', namespace='api_v2')),
    path('billing/', include(("billing.urls", "billing"), namespace='billing')),
    path('blog/', include(("blog.urls", "blog"), namespace='blog')),
    path('cart/', include(("carts.urls", "blog"), namespace='cart')),
    path('checkout/address/create/', views.checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', views.checkout_address_reuse_view, name='checkout_address_reuse'),
    path('contact/', contact_page, name='contact'),
    path('library/', LibraryView.as_view(), name='library'),
    path('marketing/', include(("marketing.urls", "marketing"), namespace='marketing')),
    path('orders/', include(("orders.urls", "orders"), namespace='orders')),
    path('payment/', include(("payment.urls", "payment"), namespace='payment')),
    path('product/', include('products.urls',namespace='product')),
    path('products/', include('products.urls', namespace='products'), name="products"),
    path('search/', include('search.urls', namespace='search')),
    path('shipping/', include('search.urls', namespace='shipping')),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    print("urlpatterns", urlpatterns)