from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import (filters, permissions,
                            status, viewsets, mixins)
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import TitleFilter
from api.permissions import (IsAdminModeratorOwnerOrReadOnly, IsAdminOnly,
                             IsAdminReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, GetTokenSerializer,
                             ReviewSerializer, SignUpSerializer,
                             TitleSerializer, UsersSerializer,
                             ReadOnlyTitleSerializer)
from reviews.models import Category, Genre, Review, Title, User


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdminOnly,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    http_method_names = ('patch', 'post', 'get', 'delete')
        # FIXME однобуквенные переменные, нужно перечислить переменные

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=(permissions.IsAuthenticated,), url_path='me')
    def get_current_user_info(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            user = request.user
            # FIXME Зачем нам тут проверка на админа?  Юзер может изменять себя
            # Один блок вложенности уйдет)
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            # FIXME else не если не админ, а если метод GET (не патч)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


# FIXME Класс здесь избыточен
@api_view(['POST'])
def api_get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    # FIXME Переделать на get_or_404. Безопасность из коробки
    username = serializer.validated_data.get('username')
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, data['confirmation_code']):
        # FIXME не совсем правильно здесь использовать RefreshToken, поскольку у нас здесь немного другой алгоритм и настоящие refresh токены не используются
        # лучше сделать from rest_framework_simplejwt.tokens import AccessToken 
        # и им воспользоваться
        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=status.HTTP_201_CREATED)
    # FIXME правильнее сделать raise ValidationError, который сам конвертируется в 400 код ответа
    # Это нужно для лучше понимания кодом программистом, что тут у нас ошибочная ситуация
    return Response(
        {'confirmation_code': 'Неверный код подтверждения!'},
        status=status.HTTP_400_BAD_REQUEST)


# FIXME Класс здесь избыточен
@api_view(['POST'])
def api_signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, _ = User.objects.get_or_create(
            **serializer.validated_data
        )
    except Exception:
        return Response(
            {'Такой username или e-mail уже используется.'},
            status=status.HTTP_400_BAD_REQUEST)
    # FIXME строчки XX-XX не нужны
    # FIXME flag - неиспользуемая переменная
    # их принято именовать как _
    user, _ = User.objects.get_or_create(username=username, email=email)
    code = default_token_generator.make_token(user)
    message = f'Здравствуйте, {username}! Ваш код подтверждения: {code}'
    # FIXME Можно упросить, не делать эту функцию, а воспользоваться встроенной 
    # from django.core.mail import send_mail
    send_mail(_, message, settings.SUPPORT_MAIL, [email])
    return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class CommonGenreCategoryViewSet(mixins.CreateModelMixin,
                                 mixins.ListModelMixin,
                                 mixins.DestroyModelMixin,
                                 viewsets.GenericViewSet):
    search_fields = ('^name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminReadOnly,)


class GenreViewSet(CommonGenreCategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CommonGenreCategoryViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))

        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
