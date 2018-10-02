from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from users import views

router = DefaultRouter()
router.register(r'users', views.UsersViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
