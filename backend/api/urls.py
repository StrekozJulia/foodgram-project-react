from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet,
                    TagViewSet,
                    IngredientViewSet,
                    RecipeViewSet)


app_name = 'api'

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews'
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
