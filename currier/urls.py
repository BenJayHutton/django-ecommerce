from django.urls import path

from .views import Currier, CurrierCreateView, CurrierDeleteView, CurrierUpdateView

urlpatterns = [
    path('', Currier.as_view(), name='home'),
    path('create/', CurrierCreateView.as_view(), name='create'),
    path('<int:pk>/update', CurrierUpdateView.as_view(), name='update'),
    path('<int:pk>/delete', CurrierDeleteView.as_view(), name='delete'),
]
