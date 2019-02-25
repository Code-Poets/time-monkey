from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from managers.models import Project
from managers.serializers import ProjectSerializer
from managers.serializers import ProjectCreateSerializer


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
        return Response({
            'projects_queryset': projects_queryset,
        })


class ProjectCreate(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'managers/project_create.html'

    def get(self, request):
        project_serializer = ProjectCreateSerializer(context={'request': request})
        return Response({'serializer': project_serializer})

    def post(self, request):
        project_serializer = ProjectCreateSerializer(data=request.data, context={'request': request})
        if not project_serializer.is_valid():
            return Response({
                'serializer': project_serializer,
                'errors': project_serializer.errors,
            })
        project_serializer.save()
        return redirect('custom-projects-list')


class ProjectDetail(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'managers/project_detail.html'

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        return Response({'project': project})


class ProjectUpdate(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'managers/project_update.html'

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project_serializer = ProjectSerializer(
            project,
            context={'request': request},
        )
        return Response({'serializer': project_serializer, 'project': project})

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project_serializer = ProjectSerializer(
            project,
            data=request.data,
            context={'request': request},
        )
        if not project_serializer.is_valid():
            return Response({
                'serializer': project_serializer,
                'project': project,
                'errors': project_serializer.errors,
            })
        project_serializer.save()
        return redirect('custom-project-detail', pk=pk)

