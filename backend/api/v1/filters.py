from django_filters import rest_framework
from recipes.models import Recipe
from rest_framework import filters


class CustomNameSearch(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(field_name='author__id')
    tags = rest_framework.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
