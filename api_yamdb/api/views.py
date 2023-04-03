from rest_framework import filters, viewsets, views, permissions, status
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from api.serializers import (CategorySerializer, GenreSerializer,
                             TitleSerializer, GetTokenSerializer,
                             NotAdminSerializer, SignUpSerializer,
                             UsersSerializer, ReviewSerializer,
                             CommentSerializer)
from api.permissions import IsAdminOnly, IsAdminModeratorOwnerOrReadOnly
from reviews.models import Category, Genre, Title, User, Review


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOnly,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    http_method_names = [
        m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=(permissions.IsAuthenticated,), url_path='me')
    def get_current_user_info(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UsersSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = NotAdminSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class APIGetToken(views.APIView):

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            return Response(
                {'username': 'Нет такого пользователя!'},
                status=status.HTTP_404_NOT_FOUND)
        if default_token_generator.check_token(user,
                                               data['confirmation_code']):
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)


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
        username_taken = User.objects.filter(username=username).exists()
        email_taken = User.objects.filter(email=email).exists()
        if email_taken and not username_taken:
            return Response('email занят', status=status.HTTP_400_BAD_REQUEST)
        if username_taken and not email_taken:
            return Response('username занят',
                            status=status.HTTP_400_BAD_REQUEST)
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
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category__slug', 'genre__slug', 'name', 'year')


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))

        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
