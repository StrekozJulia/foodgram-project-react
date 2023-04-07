from django_filters import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag

TAG_LIST = [(mod.slug, mod.name) for mod in Tag.objects.all()]


class RecipeFilter(FilterSet):
    tags = filters.MultipleChoiceFilter(
        lookup_expr='slug',
        choices=TAG_LIST
    )
    is_favorited = filters.CharFilter(field_name='is_favorited')
    is_in_shopping_cart = filters.CharFilter(field_name='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def tag_filter(self, queryset, name, value):
        print(name, value)
        return queryset


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
