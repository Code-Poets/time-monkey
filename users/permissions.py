from typing import Any

from django.http import HttpRequest
from rest_framework import permissions

from users.common.strings import PermissionsMessage
from users.models import CustomUser


class AuthenticatedAdmin(permissions.BasePermission):
    message = PermissionsMessage.NONE_ADMIN_USER

    def has_permission(self, request: HttpRequest, _view: Any) -> bool:  # pylint: disable=no-self-use
        is_user_authenticated = request.user and request.user.is_authenticated
        is_user_admin = request.user.user_type == CustomUser.UserType.ADMIN.name
        return is_user_authenticated and is_user_admin


class AuthenticatedAdminOrOwnerUser(permissions.BasePermission):
    message = PermissionsMessage.NONE_ADMIN_OR_OWNER_USER

    def has_permission(self, request: HttpRequest, view: Any) -> bool:  # pylint: disable=no-self-use
        is_user_authenticated = request.user and request.user.is_authenticated
        is_user_admin = request.user.user_type == CustomUser.UserType.ADMIN.name
        is_object_owner = view.get_object() == request.user
        return is_object_owner or (is_user_authenticated and is_user_admin)

    def has_object_permission(  # pylint: disable=no-self-use
        self, request: HttpRequest, _view: Any, obj: CustomUser
    ) -> bool:
        if request.user.is_authenticated:
            return request.user.user_type == CustomUser.UserType.ADMIN.name or obj == request.user
        else:
            return False
