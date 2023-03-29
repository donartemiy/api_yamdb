from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets

from reviews.models import Title, Genre, Category
from api.serializers import TitleSerializer, GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category__slug', 'genre__slug', 'name', 'year')


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
