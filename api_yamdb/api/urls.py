from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, TitleViewSet, GenreViewSet, APIGetToken, APISignup, UsersViewSet

app_name = 'api'

router = DefaultRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')
router.register('categories', CategoryViewSet, basename='categories')
router.register('users', UsersViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
]
