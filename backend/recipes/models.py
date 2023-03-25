from django.db import models

from django.db import models
from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        help_text='Введите название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        help_text='Введите единицы измерения ингредиента',
        max_length=200
    )


class Tag(models.Model):
    name = models.CharField(
        'Название', 
        help_text='Введите название тэга',
        max_length=200
    )
    color = models.CharField(
        'Цвет',
        help_text='Введите цвет тэга в HEX',
        max_length=7
    )
    slug = models.SlugField(
        'Идентификатор',
        help_text='Введите идентификатор',
        max_length=200
    )


class Recipe(models.Model):
    ingredients =models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags =models.ManyToManyField(Tag)
    image = models.ImageField(
        'Картинка',
        help_text='Вставьте изображение готового блюда',
        upload_to='recipes/',
        blank=True
    )
    name = models.CharField(
        'Название',
        help_text='Введите название блюда',
        max_length=200,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    text = models.TextField(
        'Текст рецепта',
        help_text='Введите текст рецепта'
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        help_text='Введите время приготовления (мин)'
    )  


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'], name='unique_recipe_ingredient'
        )]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'