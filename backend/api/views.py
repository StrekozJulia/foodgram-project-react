from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Exists, OuterRef
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart
from users.models import CustomUser, Follow
from core.mixins import UserMixin, ReadOnlyMixin, CreateDestroyMixin, ListMixin
from .permissions import UserPermission, RecipePermission
from .filters import RecipeFilter
from .serializers import (CustomUserSerializer,
                          ChangePasswordSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          ReadRecipeSerializer,
                          WriteRecipeSerializer,
                          SubscribeSerializer,
                          FollowSerializer,
                          FavoriteSerializer,
                          CartSerializer)


class CustomUserViewSet(UserMixin):

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [UserPermission, ]

    @action(["get"], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = get_object_or_404(CustomUser, pk=request.user.id)
        serializer = self.get_serializer(self.get_object)
        return Response(serializer.data)

    @action(["post"], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        self.get_object = get_object_or_404(CustomUser, pk=request.user.id)
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not self.get_object.check_password(
                serializer.data.get('current_password')
            ):
                return Response(
                    {"current_password": ["Wrong password"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.get_object.set_password(serializer.data.get("new_password"))
            self.get_object.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Просмотр, создание, редактирование и удаление рецептов"""

    permission_classes = (RecipePermission,)
    http_method_names = ('get', 'patch', 'post', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all().annotate(
            is_favorited=Exists(Favorite.objects.filter(
                favorer=self.request.user,
                favorite=OuterRef('pk'))
            ),
            is_in_shopping_cart=Exists(Cart.objects.filter(
                buyer=self.request.user,
                purchase=OuterRef('pk'))
            )
        )
        return queryset

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReadRecipeSerializer
        return WriteRecipeSerializer


class SubscriptionsViewSet(ListMixin):
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()


class SubscribeViewSet(CreateDestroyMixin):
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        user_id = self.kwargs.get("user_id")
        following = get_object_or_404(CustomUser, pk=user_id)
        serializer.save(user=self.request.user,
                        following=following)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"user_id": self.kwargs.get("user_id")}
        )
        return context

    @action(methods=['delete'], detail=False)
    def delete(self, *args, **kwargs):
        following = get_object_or_404(CustomUser,
                                      pk=self.kwargs.get("user_id"))
        if not Follow.objects.filter(user=self.request.user,
                                     following=following).exists():
            raise ValidationError(
                'Вы не подписаны на данного пользователя.'
            )
        instance = Follow.objects.filter(user=self.request.user,
                                         following=following)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CreateDestroyMixin):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get("recipe_id")
        favorite = get_object_or_404(Recipe, pk=recipe_id)
        serializer.save(favorer=self.request.user,
                        favorite=favorite)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"recipe_id": self.kwargs.get("recipe_id")}
        )
        return context

    @action(methods=['delete'], detail=False)
    def delete(self, *args, **kwargs):
        favorite = get_object_or_404(Recipe,
                                     pk=self.kwargs.get("recipe_id"))
        if not Favorite.objects.filter(favorer=self.request.user,
                                       favorite=favorite).exists():
            raise ValidationError(
                'Этого рецепта нет в избранном.'
            )
        instance = Favorite.objects.filter(favorer=self.request.user,
                                           favorite=favorite)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet(CreateDestroyMixin):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get("recipe_id")
        purchase = get_object_or_404(Recipe, pk=recipe_id)
        serializer.save(buyer=self.request.user,
                        purchase=purchase)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"recipe_id": self.kwargs.get("recipe_id")}
        )
        return context

    @action(methods=['delete'], detail=False)
    def delete(self, *args, **kwargs):
        purchase = get_object_or_404(Recipe,
                                     pk=self.kwargs.get("recipe_id"))
        if not Cart.objects.filter(buyer=self.request.user,
                                   purchase=purchase).exists():
            raise ValidationError(
                'Этого рецепта нет в корзине.'
            )
        instance = Cart.objects.filter(buyer=self.request.user,
                                       purchase=purchase)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
