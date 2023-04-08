from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, TitleViewSet,
                    GenreViewSet, api_get_token,
                    api_signup, UsersViewSet,
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

auth = [
    path('signup/', api_signup),
    path('token/', api_get_token),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    # TODO Урлы с одинаковым префиксом auth (строчки 24-25) выносим в
    # отдельный список и подключаем одним инклудом
    path('v1/auth/', include(auth))
]
