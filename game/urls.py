from rest_framework.routers import DefaultRouter
from .views import BusinessViewSet, GameViewSet

router = DefaultRouter()
router.register('catalog', BusinessViewSet, basename='business')
router.register('', GameViewSet, basename='game')
urlpatterns = router.urls
