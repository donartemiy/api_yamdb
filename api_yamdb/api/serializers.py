from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator

from reviews.models import (LIMIT_EMAIL, LIMIT_USERNAME, Category, Comment,
                            Genre, Review, Title, User)
from reviews.validators import validate_username


class UsersSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=LIMIT_USERNAME,
        # FIXME валидаторы можно не прописывать, они указаны на уровне
        # модели и сработают: как уникальность, так и validate_username
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validate_username
        ],
        # FIXME required=True дефолтное поведение
        required=True,
    )
    email = serializers.EmailField(
        max_length=LIMIT_EMAIL,
        validators=[        
            UniqueValidator(queryset=User.objects.all())    # FIXME
        ]
    )

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio')


class GetTokenSerializer(serializers.Serializer):
    # FIXME Нужно ограничение длины, а также валидация
    username = serializers.CharField(
        # FIXME required=True - дефолт
        required=True)
    # FIXME Нужно ограничение длины
    confirmation_code = serializers.CharField(
        # FIXME required=True - дефолт
        required=True)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=LIMIT_EMAIL,)
    username = serializers.CharField(
        # FIXME required=True - дефолт
        required=True,
        validators=[validate_username],
        max_length=LIMIT_USERNAME)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        queryset=Genre.objects.all(),
        slug_field='slug')
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'description', 'category', 'genre', 'year'
        )


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    # FIXME неверная конструкция. не выводится rating
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'description', 'category', 'genre', 'year', 'rating'
        )
        read_only_fields = [
            'id', 'name', 'description', 'category', 'genre', 'year', 'rating']


class ReviewSerializer(serializers.ModelSerializer):
    # FIXME По ТЗ нет необходимости выводить slug,
    # а read_only можно прописать в мете
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            title_id = self.context['view'].kwargs.get('title_id')
            title = get_object_or_404(Title, pk=title_id)
            # TODO Тут вроде не избавились от вложенности
            # остались два условия, Not не использовано
            if Review.objects.filter(author=user, title=title).exists():
                raise ValidationError('Вы не можете добавить более'
                                      'одного отзыва на произведение')
        return data

    class Meta:
        model = Review
        exclude = ['title']
        read_only_fields = (
            'id', 'author', 'pub_date',
        )


class CommentSerializer(serializers.ModelSerializer):
    # FIXME По ТЗ нет необходимости выводить slug
    # а read_only можно прописать в мете
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        exclude = ['review']
        read_only_fields = (
            'id', 'author', 'pub_date',
        )
