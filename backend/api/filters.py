from recipes.models import Recipe
from django_filters import FilterSet, filters


class RecipeFilter(FilterSet):
    # name = filters.CharFilter(field_name='name', lookup_expr='contains')
    tags = filters.CharFilter(field_name='tags__slug')
    is_favorited = filters.CharFilter(field_name='is_favorited')
    is_in_shopping_cart = filters.CharFilter(field_name='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
