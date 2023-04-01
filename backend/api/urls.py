from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet,
                    TagViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    SubscribeViewSet,
                    SubscriptionsViewSet,
                    FavoriteViewSet,
                    CartViewSet)


app_name = 'api'

router = DefaultRouter()

router.register('users/subscriptions',
                SubscriptionsViewSet,
                basename='subscriptions')
router.register('users', CustomUserViewSet, basename='users')
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet,
                basename='subscribe')

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoriteViewSet,
                basename='favorite')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                CartViewSet,
                basename='shopping_cart')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
