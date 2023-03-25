from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient, Tag

class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 5


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    # list_display = ['name']

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag)
