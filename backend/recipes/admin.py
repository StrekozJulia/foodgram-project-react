from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient, Tag, Favorite

class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 5


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = ['name', 'author']

class TagAdmin(admin.ModelAdmin):
    list_display = ['name',]

class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_filter = ['name',]

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
