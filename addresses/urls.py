from django.urls import path

from .views import AddressCreateView, AddressListView, AddressUpdateView, AddressDeleteView

app_name = 'address'

urlpatterns = [
    path('', AddressListView.as_view(), name='home'),
    path('create/', AddressCreateView.as_view(), name='create'),
    path('<int:pk>/update', AddressUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', AddressDeleteView.as_view(), name='delete'),
]