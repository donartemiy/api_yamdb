from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TitleViewSet, GenreViewSet


router = DefaultRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router.urls)),
]
