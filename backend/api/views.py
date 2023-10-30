from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Exists, OuterRef, Prefetch, Case, When, BooleanField, Value
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart
from users.models import CustomUser, Follow
from core.mixins import UserMixin, ReadOnlyMixin, CreateDestroyMixin, ListMixin
from .permissions import UserPermission, RecipePermission
from .filters import RecipeFilter, IngredientSearchFilter
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

    serializer_class = CustomUserSerializer
    permission_classes = [UserPermission, ]

    def get_queryset(self):
        queryset = CustomUser.objects.all().annotate(
            is_subscribed=Exists(Follow.objects.filter(
                user=self.request.user,
                following=OuterRef('pk'))
            )
        )
        return queryset


    @action(["get"], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.get_object = queryset.get(pk=request.user.id)
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
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Просмотр, создание, редактирование и удаление рецептов"""

    permission_classes = (RecipePermission, )
    http_method_names = ('get', 'patch', 'post', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Recipe.objects.all().annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    favorer=self.request.user,
                    favorite=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(Cart.objects.filter(
                    buyer=self.request.user,
                    purchase=OuterRef('pk'))
                )
            ).order_by('-pub_date').prefetch_related(Prefetch(
                'author',
                queryset=CustomUser.objects.all().annotate(
                    is_subscribed=Exists(Follow.objects.filter(
                        user=self.request.user,
                        following=OuterRef('pk'))
                    )
                ),
                to_attr='annotated_author'))
        else:
            queryset = Recipe.objects.all().order_by(
                '-pub_date'
            ).prefetch_related(Prefetch(
                'author',
                queryset=CustomUser.objects.all().annotate(
                    is_subscribed=Value(False, output_field=BooleanField())
                ),
                to_attr='annotated_author'))
        return queryset

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReadRecipeSerializer
        return WriteRecipeSerializer


class SubscriptionsViewSet(ListMixin):
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all().prefetch_related(
            Prefetch(
                "following",
                queryset=CustomUser.objects.all().annotate(
                    is_subscribed=Exists(Follow.objects.filter(
                        user=self.request.user,
                        following=OuterRef('pk'))
                    ))
            ))


class SubscribeViewSet(CreateDestroyMixin):
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_user_queryset(self):
        return CustomUser.objects.all().annotate(
            is_subscribed=Exists(Follow.objects.filter(
                user=self.request.user,
                following=OuterRef('pk'))
            ))

    def perform_create(self, serializer):
        user_id = self.kwargs.get("user_id")
        authors = self.get_user_queryset()
        following = get_object_or_404(authors, pk=user_id)
        following.is_subscribed = True
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
        favorite.times_added_to_favorite -= 1
        favorite.save()
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

@api_view(['GET', ])
def download_purchase_list(request):
    """выводит список покупок в формате .pdf"""

    user = request.user
    recipes_in_cart = enumerate(user.purchases.all())
    ingredient_dict = {}
    for res in recipes_in_cart:
        ingr_in_recipe_list = res[1].recipe_ingredient.all()
        for ingr in enumerate(ingr_in_recipe_list):
            if ingr[1].ingredient.name not in ingredient_dict:
                ingredient_dict[ingr[1].ingredient.name] = [
                    int(ingr[1].amount),
                    ingr[1].ingredient.measurement_unit
                ]
            else:
                ingredient_dict[ingr[1].ingredient.name][0] += (
                    int(ingr[1].amount)
                )

    file_data = 'Список ингредиентов для покупки:\n'
    for elm in ingredient_dict:
        file_data += f'- {elm} ({ingredient_dict[elm][1]}): {ingredient_dict[elm][0]}\n'
    response = FileResponse(file_data,
                            status=status.HTTP_201_CREATED)
    response['Content-type'] = 'application/text charset=utf-8',
    return response
