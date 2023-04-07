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
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты и их количество',
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
        help_text="Выберите тэги",
        blank=False,
    )
    image = models.ImageField(
        'Иллюстрация',
        help_text='Вставьте изображение готового блюда',
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
    favorers = models.ManyToManyField(
        CustomUser,
        through='Favorite',
        through_fields=('favorite', 'favorer'),
        related_name='favorites',
        verbose_name='Избранные рецепты',
        help_text='Выберите избранные рецепты',
        blank=True,
    )
    buyers = models.ManyToManyField(
        CustomUser,
        through='Cart',
        through_fields=('purchase', 'buyer'),
        related_name='purchases',
        verbose_name='Список рецептов в корзине',
        help_text='Выберите рецепты для покупки',
        blank=True,
    )
    times_added_to_favorite = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    amount = models.IntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient'
        )]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    favorer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorer',
        blank=False,
        null=False
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='favorite',
        blank=False,
        null=False
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            recipe = Recipe.objects.get(pk=self.favorite.pk)
            recipe.times_added_to_favorite += 1
            recipe.save()
        super(Favorite, self).save()

    def delete(self, *args, **kwargs):
        recipe = Recipe.objects.get(pk=self.favorite.pk)
        recipe.times_added_to_favorite -= 1
        recipe.save()
        super(Favorite, self).delete()

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['favorer', 'favorite'], name='unique_favorite'
        )]


class Cart(models.Model):
    buyer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Покупатель',
        related_name='buyer',
        blank=False,
        null=False
    )
    purchase = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт для покупки',
        related_name='purchase',
        blank=False,
        null=False
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['buyer', 'purchase'], name='unique_purchase'
        )]

    def __str__(self):
        return f'Рецепт {self.purchase.name} в корзине {self.buyer.username}'
