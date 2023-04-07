from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient, Tag, Favorite, Cart


class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 5


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = ['name', 'author', 'times_added_to_favorite']
    list_filter = ['name', 'author', 'tags']


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', ]


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_filter = ['name', ]


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['favorer', 'favorite']

    def delete_queryset(self, request, object):
        for elm in enumerate(object):
            elm[1].delete()


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Cart)
