from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.common.strings import ProjectReportListStrings
from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
from employees.forms import ProjectJoinForm
from employees.models import Report
from employees.serializers import ReportSerializer
from managers.models import Project


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        return Report.objects.filter(author=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


def query_as_dict(query_set):
    dictionary = {}
    for record in query_set:
        key = record.date
        dictionary.setdefault(key, [])
        dictionary[key].append(record)
    for key in dictionary.keys():
        hours_per_day = hours_per_day_counter(dictionary[key])
        dictionary[key].append(decimal_to_hours_string(hours_per_day))
    return dictionary


def hours_to_minutes(work_hours):
    return (work_hours % 1 + Decimal('0.60') * (work_hours // 1)) * 100


def minutes_to_hours(minutes):
    return (minutes / 100) // Decimal('0.60') + (minutes / 100) % Decimal('0.60')


def hours_per_day_counter(reports):
    minutes_sum = 0
    for report in reports:
        minutes_sum = minutes_sum + hours_to_minutes(report.work_hours)
    hours_sum = minutes_to_hours(minutes_sum)
    return hours_sum


def hours_per_month_counter(dictionary):
    minutes_sum = Decimal(0)
    for reports in dictionary.values():
        minutes_sum = minutes_sum + hours_to_minutes(hours_string_to_decimal(reports[-1]))
    hours_sum = minutes_to_hours(minutes_sum)
    return hours_sum


def decimal_to_hours_string(decimal):
    return decimal.to_eng_string().replace('.', ':')


def hours_string_to_decimal(hours_string):
    return Decimal(hours_string.replace(':', '.'))


def parse_month_to_string(month):
    if int(month) < 10:
        return f'0{month}'
    return str(month)


def get_title_date(year, month):
    return f'{parse_month_to_string(month)}/{year}'


class ReportList(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'employees/report_list.html'
    reports_dict = {}
    project_form = ''
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        return Report.objects.filter(author=self.request.user).order_by('-date', 'project__name')

    def _add_project(self, serializer, project):
        project.members.add(self.request.user)
        project.full_clean()
        project.save()
        serializer.fields['project'].initial = project

    def _create_serializer(self):
        reports_serializer = ReportSerializer(context={'request': self.request}, )
        reports_serializer.fields['project'].queryset = \
            Project.objects.filter(
                members__id=self.request.user.id
        ).order_by('name')
        return reports_serializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.reports_dict = query_as_dict(self.get_queryset())
        self.project_form = ProjectJoinForm(
            queryset=Project.objects.exclude(members__id=self.request.user.id).order_by('name'),
        )

    def get(self, _request):
        return Response({
            'serializer': self._create_serializer(),
            'reports_dict': self.reports_dict,
            'UI_text': ReportListStrings,
            'project_form': self.project_form,
            'monthly_hours': decimal_to_hours_string(hours_per_month_counter(self.reports_dict)),
        })

    def post(self, request):
        reports_serializer = ReportSerializer(data=request.data, context={'request': request})
        if 'join' in request.POST:
            project_id = request.POST['projects']
            project = Project.objects.get(id=int(project_id))
            self._add_project(serializer=reports_serializer, project=project)
            self.project_form = ProjectJoinForm(
                queryset=Project.objects.exclude(members__id=self.request.user.id).order_by('name'),
            )
            reports_serializer = self._create_serializer()
            reports_serializer.fields['project'].initial = project
            return Response({
                'serializer': reports_serializer,
                'reports_dict': self.reports_dict,
                'UI_text': ReportListStrings,
                'project_form': self.project_form,
                'monthly_hours': decimal_to_hours_string(hours_per_month_counter(self.reports_dict)),
            })

        elif not reports_serializer.is_valid():
            return Response({
                'serializer': reports_serializer,
                'reports_dict': self.reports_dict,
                'errors': reports_serializer.errors,
                'UI_text': ReportListStrings,
                'project_form': self.project_form,
                'monthly_hours': decimal_to_hours_string(hours_per_month_counter(self.reports_dict)),
            })
        reports_serializer.save(author=self.request.user)
        return Response({
            'serializer': self._create_serializer(),
            'reports_dict': query_as_dict(self.get_queryset()),
            'UI_text': ReportListStrings,
            'project_form': self.project_form,
            'monthly_hours': decimal_to_hours_string(hours_per_month_counter(self.reports_dict)),
        }, status=201)


class ReportDetail(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'employees/report_detail.html'
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def _create_serializer(self, report, data=None):
        if data is None:
            reports_serializer = ReportSerializer(report, context={'request': self.request},)
        else:
            reports_serializer = ReportSerializer(report, data=data, context={'request': self.request}, )
        reports_serializer.fields['project'].queryset = \
            Project.objects.filter(
                members__id=report.author.pk
        ).order_by('name')
        return reports_serializer

    def get(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        serializer = self._create_serializer(report)
        return Response({
            'serializer': serializer,
            'report': report,
            'UI_text': ReportDetailStrings,
        })

    def post(self, request, pk):
        if "discard" not in request.POST:
            report = get_object_or_404(Report, pk=pk)
            serializer = self._create_serializer(report, request.data)
            if not serializer.is_valid():
                return Response({
                    'serializer': serializer,
                    'report': report,
                    'errors': serializer.errors,
                    'UI_text': ReportDetailStrings,
                })
            serializer.save()
        return redirect('custom-report-list')


def delete_report(_request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.delete()
    return redirect('custom-report-list')


class ProjectReportList(APIView):
    serializer_class = ReportSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'employees/project_report_list.html'
    user_interface_text = ProjectReportListStrings
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self, project_pk, author_pk, year, month):
        return Report.objects.filter(
            project=project_pk,
            author=author_pk,
            date__year=year,
            date__month=month,
        ).order_by('-date')

    def include_users_in_reports_dict(self, project, year, month):
        reports_dict = {}
        for user in project.members.all():
            queryset = self.get_queryset(project_pk=project.pk, author_pk=user.pk, year=year, month=month)
            user_reports_dict = query_as_dict(queryset)
            key = user.email
            reports_dict[key] = [user_reports_dict, decimal_to_hours_string(hours_per_month_counter(user_reports_dict))]
        return reports_dict

    def get(self, _request, pk, year, month):
        project = get_object_or_404(Project, pk=pk)
        reports_dict = self.include_users_in_reports_dict(project, year, month)
        return Response({
            'project_name': project.name,
            'reports_dict': reports_dict,
            'UI_text': self.user_interface_text,
            'title_date': get_title_date(year, month),
            'month_navigator_params': ['project-report-list', int(year), int(month), pk],
        })

    def post(self, request, pk, year, month):
        year = request.POST['year']
        month = request.POST['month']
        return redirect('project-report-list', pk, year, month)
