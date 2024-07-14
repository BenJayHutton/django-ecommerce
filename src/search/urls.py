from django.urls import path

from .views import SearchProductView, SearchApiProductView

app_name = 'search'

urlpatterns = [
    path('', SearchProductView.as_view(), name='query'),
    path('api/', SearchApiProductView.as_view(), name='api'),
]