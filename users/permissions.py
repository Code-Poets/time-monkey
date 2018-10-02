from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    message = 'You are not allowed to enter - only for admin.'
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'Admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    message = "It's none of your business."
    def has_permission(self, request, view):
        if view.get_object() == request.user:
            return True
        return request.user and request.user.is_authenticated and request.user.user_type == 'Admin'
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.user_type == 'Admin'
