# from core.mixins import ListCreateDestroy
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
# from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils
from djoser.conf import settings
from rest_framework import filters, permissions, status, views, viewsets, generics
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from recipes.models import Tag, Ingredient, Recipe
from users.models import CustomUser
from core.mixins import UserMixin, ReadOnlyMixin, RecipeMixin
from .permissions import UserPermission, RecipePermission

# from .filters import TitleFilter
# from .permissions import (AdminOrReadOnly, IsAdmin,
#                           IsAuthorAdminModeratorOrReadOnly)
from .serializers import (CustomUserSerializer,
                          ChangePasswordSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          RecipeSerializer)


class CustomUserViewSet(UserMixin):

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [UserPermission,]

    @action(["get",], detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.get_object = get_object_or_404(CustomUser, pk=request.user.id)
        serializer = self.get_serializer(self.get_object)
        return Response(serializer.data)

    @action(["post",], detail=False, permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        self.get_object = get_object_or_404(CustomUser, pk=request.user.id)
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not self.get_object.check_password(serializer.data.get('current_password')):
                return Response({"current_password": ["Wrong password"]}, status=status.HTTP_400_BAD_REQUEST)
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


class RecipeViewSet(RecipeMixin):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [RecipePermission,]
