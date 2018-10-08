"""
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from users import views

router = DefaultRouter()
router.register(r'users', views.UsersViewSet),
router.register(r'user', views.UserViewSet),

urlpatterns = [
    url(r'^', include(router.urls))
]
"""

from users.views import UserViewSet, UsersViewSet, api_root
from rest_framework import renderers
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url

users_list = UsersViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

users_detail = UsersViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = format_suffix_patterns([
    url(r'^$', api_root),
    url(r'^users/$', users_list, name='users-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', users_detail, name='users-detail'),
    url(r'^account/(?P<pk>[0-9]+)/$', user_detail, name='user-detail')
])
