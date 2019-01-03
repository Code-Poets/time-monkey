from django.urls import include
from django.urls import path
from rest_framework import routers
from managers import views


router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('projects/', views.ProjectsList.as_view(), name='custom-projects-list'),
    path('projects/create/', views.ProjectCreate.as_view(), name='custom-project-create'),
    path('projects/<int:pk>/', views.ProjectDetail.as_view(), name='custom-project-detail'),
    path('projects/<int:pk>/update', views.ProjectUpdate.as_view(), name='custom-project-update'),
    path('projects/<int:pk>/delete', views.delete_project, name='custom-project-delete'),
    path('api/', include(router.urls)),
]
