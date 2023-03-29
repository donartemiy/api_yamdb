from rest_framework import filters, viewsets

from api.serializers import GenreSerializer, TitleSerializer
from reviews.models import Genre, Title


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('category__slug', 'genre__slug', 'name', 'year')


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
