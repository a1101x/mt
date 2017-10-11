from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Permissions for superadmin user only.
    """
    def has_permission(self, request, view):
        return (
            request.user and is_authenticated(request.user) and request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Permissions for superadmin or readonly mode.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and is_authenticated(request.user) and request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or
            request.user and is_authenticated(request.user) and request.user.is_superuser
        ) 


class IsAdminOrOwnerOrReadOnly(BasePermission):
    """
    Permissions for superadmin, owner of object or readonly mode.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and is_authenticated(request.user) and request.user.is_superuser or
            request.user and is_authenticated(request.user)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or
            request.user and is_authenticated(request.user) and request.user.is_superuser or
            request.user and is_authenticated(request.user) and obj.user == request.user
        ) 


class IsOwnerOrReadOnly(BasePermission):
    """
    Permissions for owner or readonly mode.
    """
    def has_permission(self, request, view):
        return (
            is_authenticated(request.user)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS or
            obj.user == request.user
        ) 
