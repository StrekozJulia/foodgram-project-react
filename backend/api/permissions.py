from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """Проверка: авторизован ли пользователь."""
    message = ('Данное действие доступно только '
               'авторизованным пользователям.')
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated