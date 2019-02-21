from django.urls import include
from django.urls import path
from rest_framework import routers
from managers import views


router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('projects/', views.ProjectsList.as_view(), name='projects-list'),
    path('api/', include(router.urls)),
]
