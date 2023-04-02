from rest_framework import serializers

from reviews.models import Genre, Title, User, Category, LIMIT_USERNAME, LIMIT_EMAIL
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
        max_length=LIMIT_EMAIL,)
    username = serializers.CharField(
        required=True,
        validators=[validate_username],
        max_length=LIMIT_USERNAME)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='slug')

    class Meta:
        model = Title
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'