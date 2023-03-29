from rest_framework import serializers

from reviews.models import Genre, Title


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
