from users.models import CustomUser
from users.serializers import UserDetailSerializer, UserListSerializer, UserCreateSerializer, UserUpdateSerializer, UserSerializer
from rest_framework import viewsets
from rest_framework import permissions
from users.permissions import IsAdminUser, IsOwnerOrAdmin


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'retrieve':
            return UserDetailSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'update':
            return UserCreateSerializer
        return UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsOwnerOrAdmin,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        if self.action == 'update':
            return UserUpdateSerializer
        return UserSerializer
