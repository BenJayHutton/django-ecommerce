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
from .views import DefaultHomePage

app_name = 'eCommerce'

urlpatterns = [
    path('', DefaultHomePage.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts'), name='accounts'),
    path('api/', include('api.urls', namespace='api')),
    path('api/v2/', include('eCommerce.routers', namespace='api_v2')),
    path('billing/', include(("billing.urls", "billing"), namespace='billing')),
    path('product/', include('products.urls',namespace='product')),
    path('products/', include('products.urls', namespace='products'), name="products"),
    path('search/', include('search.urls', namespace='search')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)