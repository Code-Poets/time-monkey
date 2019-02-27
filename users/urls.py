from rest_framework.urlpatterns import format_suffix_patterns

from django.conf.urls import url
from django.contrib.auth import views as django_views
from users import views


users_list = views.UsersViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

users_detail = views.UsersViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

user_account_detail = views.UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = format_suffix_patterns([
    url(r'^api/$', views.api_root),
    url(r'^api/users/$', users_list, name='users-list'),
    url(r'^api/users/(?P<pk>[0-9]+)/$', users_detail, name='users-detail'),
    url(r'^api/account/(?P<pk>[0-9]+)/$', user_account_detail, name='user-account-detail'),
    url(r'^$', views.index, name='home'),
    #Override login view
    url('login/', views.CustomUserLoginView.as_view(), name='login'),
    #Use django login system
    url('logout/', django_views.LogoutView.as_view(), name='logout'),
    url('password_change/', django_views.PasswordChangeView.as_view(), name='password_change'),
    url('password_change/done/', django_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url('password_reset/', django_views.PasswordResetView.as_view(), name='password_reset'),
    url('password_reset/done/', django_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url('reset/<uidb64>/<token>/', django_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url('reset/done/', django_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    url(r'^signup/$', views.SignUp.as_view(), name='signup'),
    url(r'^user/(?P<pk>[0-9]+)/$', views.UserUpdate.as_view(), name='custom-user-update'),
    url(r'^user/create/$', views.UserCreate.as_view(), name='custom-user-create'),
    url(r'^users/$', views.UserList.as_view(), name='custom-users-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserUpdateByAdmin.as_view(), name='custom-user-update-by-admin'),
])
