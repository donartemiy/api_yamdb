from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, _):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminReadOnly(permissions.BasePermission):
    def has_permission(self, request, _):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin)


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, _, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)

    def has_permission(self, request, _):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)
