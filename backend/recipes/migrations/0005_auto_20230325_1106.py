# Generated by Django 2.2.16 on 2023-03-25 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230325_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Вставьте изображение готового блюда', upload_to='recipes/', verbose_name='Иллюстрация'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите ингредиенты и их количество', through='recipes.RecipeIngredient', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите тэги', to='recipes.Tag', verbose_name='Тэги'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(help_text='Введите текстовый идентификатор (слаг)', max_length=200, unique=True, verbose_name='Текстовый идентификатор'),
        ),
    ]
