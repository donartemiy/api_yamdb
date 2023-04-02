from rest_framework import serializers

from reviews.models import Category, Genre, Title, User
from reviews.validators import validate_username


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('all')


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('all')


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True)
    confirmation_code = serializers.CharField(
        required=True)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,)
    username = serializers.CharField(
        required=True,
        validators=[validate_username],
        max_length=150)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='slug')
    category = serializers.SlugRelatedField(
        many=False,
        queryset=Category.objects.all(),
        slug_field='slug')

    class Meta:
        model = Title
        fields = '__all__'
