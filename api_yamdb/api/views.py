from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import (filters, permissions,
                            status, views, viewsets, mixins)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import TitleFilter
from api.permissions import (IsAdminModeratorOwnerOrReadOnly, IsAdminOnly,
                             IsAdminReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, GetTokenSerializer,
                             NotAdminSerializer, ReviewSerializer,
                             SignUpSerializer, TitleSerializer,
                             UsersSerializer, ReadOnlyTitleSerializer)
from reviews.models import Category, Genre, Review, Title, User


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdminOnly,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    http_method_names = [
        # FIXME однобуквенные переменные, нужно перечислить переменные
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=(permissions.IsAuthenticated,), url_path='me')
    def get_current_user_info(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            # FIXME Зачем нам тут проверка на админа?  Юзер может изменять себя
            # Один блок вложенности уйдет)
            if request.user.is_admin:
                serializer = UsersSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            # FIXME else не если не админ, а если метод GET (не патч)
            else:
                serializer = NotAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


# FIXME Класс здесь избыточен
class APIGetToken(views.APIView):

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # FIXME Переделать на get_or_404. Безопасность из коробки
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response(
                {'username': 'Нет такого пользователя!'},
                status=status.HTTP_404_NOT_FOUND)
        if default_token_generator.check_token(user,
                                               data['confirmation_code']):
            # FIXME не совсем правильно здесь использовать RefreshToken, поскольку у нас здесь немного другой алгоритм и настоящие refresh токены не используются
            # лучше сделать from rest_framework_simplejwt.tokens import AccessToken 
            # и им воспользоваться
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        # FIXME правильнее сделать raise ValidationError, который сам конвертируется в 400 код ответа
        # Это нужно для лучше понимания кодом программистом, что тут у нас ошибочная ситуация
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)


# FIXME Класс здесь избыточен
class APISignup(views.APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        # FIXME строчки XX-XX не нужны
        # get_or_create на строчке 100 вызовет ошибку, если почта и логин занят
        # достаточно лишь её перехватить и обработать
        username_taken = User.objects.filter(username=username).exists()
        email_taken = User.objects.filter(email=email).exists()
        if email_taken and not username_taken:
            return Response('email занят', status=status.HTTP_400_BAD_REQUEST)
        if username_taken and not email_taken:
            return Response('username занят',
                            status=status.HTTP_400_BAD_REQUEST)
        # FIXME flag - неиспользуемая переменная
        # их принято именовать как _
        user, flag = User.objects.get_or_create(
            username=username,
            email=email)
        code = default_token_generator.make_token(user)
        email_body = (
            f'Здраствуте, {user.username}.'
            f'\nКод подтверждения: {code}'
        )
        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Код подтверждения '
        }
        # FIXME Можно упросить, не делать эту функцию, а воспользоваться встроенной 
        # from django.core.mail import send_mail
        self.send_email(data)
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
