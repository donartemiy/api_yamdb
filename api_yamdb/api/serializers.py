from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from django.db.models import Avg

from reviews.models import (LIMIT_EMAIL, LIMIT_USERNAME, Category, Comment,
                            Genre, Review, Title, User)
from reviews.validators import validate_username


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=LIMIT_USERNAME, validators=[validate_username],)
    confirmation_code = serializers.CharField()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=LIMIT_EMAIL,)
    username = serializers.CharField(
        validators=[validate_username], max_length=LIMIT_USERNAME)


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
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'description', 'category', 'genre', 'year', 'rating'
        )
        read_only_fields = [
            'id', 'name', 'description', 'category', 'genre', 'year', 'rating']

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        return rating if not rating else round(rating, 0)


class ReviewSerializer(serializers.ModelSerializer):
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
