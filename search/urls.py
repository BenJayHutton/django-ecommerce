from django.urls import path

from .views import (
        SearchProductView,
        SearchTagView
        )

urlpatterns = [
    path('query/', SearchProductView.as_view(), name='query'),
    path('tag/', SearchTagView.as_view(), name='tag'),
]
