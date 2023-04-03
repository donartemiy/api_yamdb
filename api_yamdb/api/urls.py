from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, TitleViewSet,
                    GenreViewSet, APIGetToken,
                    APISignup, UsersViewSet,
                    CommentViewSet, ReviewViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')
router.register('categories', CategoryViewSet, basename='categories')
router.register('users', UsersViewSet, basename='users')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                r'/comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
]
