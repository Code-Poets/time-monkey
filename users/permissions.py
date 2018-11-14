from rest_framework import permissions
from users.models import CustomUser


class IsReportAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.user_type == CustomUser.UserType.MANAGER.value
        return False


class IsManagerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.user_type == CustomUser.UserType.MANAGER.value
        return False
