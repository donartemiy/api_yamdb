from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import IntegerField
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from reviews.models import (Category, Comment,
                            Genre, Review, Title, User)
from reviews.validators import validate_username


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class UserEditSerializer(UsersSerializer):
    class Meta(UsersSerializer.Meta):
        read_only_fields = ('role',)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.LIMIT_USERNAME, validators=[validate_username],)
    confirmation_code = serializers.CharField()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=settings.LIMIT_EMAIL,)
    username = serializers.CharField(
        validators=[validate_username], max_length=settings.LIMIT_USERNAME)


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
            'id', 'name', 'description', 'category', 'genre', 'year',
        )


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'description', 'category', 'genre', 'year', 'rating'
        )
        read_only_fields = (
            'id', 'name', 'description', 'category', 'genre', 'year', 'rating')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        exclude = ('title',)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(author=user, title=title).exists():
            raise ValidationError('Вы не можете добавить более'
                                  'одного отзыва на произведение')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        exclude = ('review',)
