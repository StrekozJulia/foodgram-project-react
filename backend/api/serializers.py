# import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import base64
from django.core.files.base import ContentFile
from rest_framework.generics import get_object_or_404

from users.models import CustomUser, Follow
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            Favorite,
                            Cart)


class CustomUserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=CustomUser.objects.all(),
            message='username должен быть уникальным')]
    )

    password = serializers.CharField(
        required=True,
        write_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password', 'is_subscribed')

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj,
            following=self.context['request'].user
        ).exists()


class ChangePasswordSerializer(serializers.Serializer):
    """сериализотор для смены пароля пользователя."""

    model = CustomUser

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецептах"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецептах"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    author = CustomUserSerializer()
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = ReadRecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'tags', 'author', 'ingredients',
                            'is_favorited', 'is_in_shopping_cart',
                            'name', 'image', 'text', 'cooking_time')


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор для сокращенного отображения рецептов."""

    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = WriteRecipeIngredientSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = ('name', 'author', 'ingredients', 'tags',
                  'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe_instance = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe_instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )

        recipe_instance.tags.set(tags_data)
        recipe_instance.save()

        return recipe_instance

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        list_of_recipe_ingr = RecipeIngredient.objects.filter(
            recipe=self.instance
        )
        for res_ingr in list_of_recipe_ingr:
            res_ingr.delete()

        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=self.instance,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )

        instance.tags.set(tags_data)
        instance.save()

        return self.instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance=instance).data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок на авторов"""

    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeMiniSerializer(many=True,
                                   source='following.recipes')
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        author = obj.following
        return Follow.objects.filter(
            user=author,
            following=self.context['request'].user
        ).exists()

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и удаления подписок на авторов."""

    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    following = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow

    def validate_self_following(self):
        """Проверка невозможности подписки на самого себя."""

        following = int(self.context['user_id'])
        if following == self.context['request'].user.pk:
            raise serializers.ValidationError(
                'Не допускается подписка на самого себя.'
            )

    def validate_unique_following(self):
        """Проверка уникальности подписки."""

        user = self.context['request'].user
        following = get_object_or_404(CustomUser, pk=self.context['user_id'])
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя.'
            )

    def validate(self, attrs):
        self.validate_self_following()
        self.validate_unique_following()
        return attrs

    def to_representation(self, instance):
        return FollowSerializer(instance=instance).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и удаления рецепта в избранное."""

    favorer = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    favorite = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = ('favorer', 'favorite')
        model = Favorite

    def validate_unique_favorite(self):
        """Проверка уникальности рецепта в избранном."""

        favorer = self.context['request'].user
        favorite = get_object_or_404(Recipe, pk=self.context['recipe_id'])
        if Favorite.objects.filter(favorer=favorer,
                                   favorite=favorite).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке избранного.'
            )

    def validate(self, attrs):
        self.validate_unique_favorite()
        return attrs

    def to_representation(self, instance):
        recipe = instance.favorite
        return RecipeMiniSerializer(instance=recipe).data


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и удаления рецепта в корзину."""

    buyer = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    purchase = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        fields = ('buyer', 'purchase')
        model = Cart

    def validate_unique_purchase(self):
        """Проверка уникальности рецепта в избранном."""

        buyer = self.context['request'].user
        purchase = get_object_or_404(Recipe, pk=self.context['recipe_id'])
        if Cart.objects.filter(buyer=buyer, purchase=purchase).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в корзине.'
            )

    def validate(self, attrs):
        self.validate_unique_purchase()
        return attrs

    def to_representation(self, instance):
        recipe = instance.purchase
        return RecipeMiniSerializer(instance=recipe).data
