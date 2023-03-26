from django.db import models

from django.db import models
from users.models import CustomUser


NAME_LEN = 200
SLUG_LEN = 200
HEX_LEN = 7
UNIT_LEN = 200

class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        help_text='Введите название ингредиента',
        blank=False,
        null=False,
        max_length=NAME_LEN,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        help_text='Введите единицы измерения ингредиента',
        blank=False,
        null=False,
        max_length=UNIT_LEN
    )

    def __str__(self):
        return f'ингредиент: {self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название', 
        help_text='Введите название тэга',
        unique=True,
        blank=False,
        null=False,
        max_length=NAME_LEN
    )
    color = models.CharField(
        'Цвет',
        help_text='Введите цвет тэга в HEX',
        unique=True,
        blank=False,
        null=False,
        max_length=HEX_LEN
    )
    slug = models.SlugField(
        'Текстовый идентификатор',
        help_text='Введите текстовый идентификатор (слаг)',
        unique=True,
        blank=False,
        null=False,
        max_length=SLUG_LEN
    )

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты и их количество',
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        help_text="Выберите тэги",
        blank=False,
        null=False
    )
    image = models.ImageField(
        'Иллюстрация',
        help_text='Вставьте изображение готового блюда',
        upload_to='data/images/',
        blank=False,
        null=False
    )
    name = models.CharField(
        'Название',
        help_text='Введите название блюда',
        blank=False,
        null=False,
        max_length=NAME_LEN,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text="Укажите автора рецепта",
        related_name='recipes',
        blank=False,
        null=False
    )
    text = models.TextField(
        'Текст рецепта',
        help_text='Введите текст рецепта',
        blank=False,
        null=False,
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        help_text='Введите время приготовления (мин)',
        blank=False,
        null=False,
    )

    def __str__(self):
        return f'Рецепт "{self.name}"'


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