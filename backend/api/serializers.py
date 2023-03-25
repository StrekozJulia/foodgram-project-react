# import datetime
from rest_framework import serializers
# from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
# from django.contrib.auth import get_user_model
# import base64
# from django.core.files.base import ContentFile

# from recipes.models import Recipe, Ingredient
from users.models import CustomUser
from .validators import UsernameValidator


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

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

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


class ChangePasswordSerializer(serializers.Serializer):
    """сериализотор для смены пароля пользователя."""
    
    model = CustomUser

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


# class UserProfileSerializer(CustomUsersSerializer):

#     class Meta:
#         model = CustomUser
#         fields = (
#             'username', 'email', 'first_name', 'last_name', 'bio', 'role'
#         )
#         read_only_fields = ('role',)


# class SingUpSerializer(serializers.Serializer):

#     email = serializers.EmailField(
#         required=True,
#     )
#     username = serializers.CharField(
#         required=True,
#     )

#     def validate_username(self, value):
#         if value == 'me':
#             raise serializers.ValidationError(
#                 "Имя пользователя не может быть 'me'"
#             )
#         return value

#     def validate(self, attrs):
#         if User.object.filter(
#                 username=attrs.get('username'),
#                 email=attrs.get('email')).exists():
#             pass
#         elif (User.object.filter(username=attrs.get('username')).exists()
#                 and not User.object.filter(email=attrs.get('email')).exists()):
#             raise serializers.ValidationError(
#                 "Пользователь с таким username уже есть."
#             )
#         elif (User.object.filter(email=attrs.get('email')).exists()
#                 and not User.object.filter(
#                     username=attrs.get('username')).exists()):
#             raise serializers.ValidationError(
#                 "Пользователь с таким email уже есть."
#             )
#         return attrs



# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#         return super().to_internal_value(data)


# class RecipeSerializer(serializers.ModelSerializer):
#     author = SlugRelatedField(slug_field='username', read_only=True)
#     image = Base64ImageField(required=False, allow_null=True)

#     class Meta:
#         fields = '__all__'
#         model = Recipe