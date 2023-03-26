from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """Проверка: авторизован ли пользователь."""
    message = ('Данное действие доступно только '
               'авторизованным пользователям.')
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated

class RecipePermission(permissions.BasePermission):
    """Проверка прав для действий с рецептами."""
    message = ('Редактирование и удаление рецептов '
               'доступно только их авторам.')
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )
    
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )