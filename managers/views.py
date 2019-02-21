from django.db.models import Count
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from managers.models import Project
from managers.serializers import ProjectSerializer
from managers.serializers import ProjectsListSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectsList(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'managers/projects_list.html'

    def get_queryset(self):
        return Project.objects.all().order_by('id')

    def get(self, request):
        projects_queryset = self.get_queryset()
        if request.GET.get('sort'):
            if 'members' in request.GET.get('sort'):
                projects_queryset = Project.objects.annotate(members_count=Count('members')) \
                    .order_by(request.GET.get('sort'))
            else:
                projects_queryset = projects_queryset.order_by(request.GET.get('sort'))
        projects_serializer = ProjectsListSerializer(context={'request': request})
        return Response({
            'serializer': projects_serializer,
            'projects_queryset': projects_queryset,
        })
