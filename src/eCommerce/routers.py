from rest_framework.routers import DefaultRouter

from products.viewsets import ProductViewSet

router = DefaultRouter()

app_name = 'api_v2'

router.register('products-abc', ProductViewSet, basename = 'products')
urlpatterns = router.urls