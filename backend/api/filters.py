from django_filters import FilterSet, filters
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter

TAG_LIST = [(mod[1].slug, mod[1].name) for mod in enumerate(Tag.objects.all())]


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
