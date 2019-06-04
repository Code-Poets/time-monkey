import datetime
import logging
from typing import Any

from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.http.response import HttpResponseRedirect
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from rest_framework import permissions
from rest_framework import viewsets

from employees.common.constants import ExcelGeneratorSettingsConstants
from employees.common.exports import generate_xlsx_for_project
from employees.common.exports import generate_xlsx_for_single_user
from employees.common.strings import AdminReportDetailStrings
from employees.common.strings import AuthorReportListStrings
from employees.common.strings import ProjectReportDetailStrings
from employees.common.strings import ProjectReportListStrings
from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
from employees.forms import ProjectJoinForm
from employees.forms import ReportForm
from employees.models import Report
from employees.serializers import ReportSerializer
from managers.models import Project
from users.models import CustomUser
from utils.decorators import check_permissions
from utils.mixins import UserIsAuthorOfCurrentReportMixin
from utils.mixins import UserIsManagerOfCurrentProjectMixin
from utils.mixins import UserIsManagerOfCurrentReportProjectMixin

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        return Report.objects.filter(author=self.request.user).order_by("-date")

    def perform_create(self, serializer: ReportSerializer) -> None:
        logger.info(f"Perform create method for user: {self.request.user}")
        serializer.save(author=self.request.user)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(
        allowed_user_types=[
            CustomUser.UserType.EMPLOYEE.name,
            CustomUser.UserType.MANAGER.name,
            CustomUser.UserType.ADMIN.name,
        ]
    ),
    name="dispatch",
)
class ReportCreateView(CreateView):
    model = Report
    form_class = ReportForm
    template_name = "employees/report_list.html"
    extra_context = {"UI_text": ReportListStrings}

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user_joined_to_project = "join" in request.POST
        if user_joined_to_project:
            form = ProjectJoinForm(
                queryset=Project.objects.exclude(members__id=self.request.user.id).order_by("name"), data=request.POST
            )
            if form.is_valid():
                project = Project.objects.get(id=int(self.request.POST["projects"]))
                project.members.add(self.request.user)
                project.full_clean()
                project.save()
                return self.form_valid_for_join_project()
            else:
                return self.form_invalid_for_join_project(form)
        else:
            return super().post(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["object_list"] = (
            super().get_queryset().filter(author=self.request.user).order_by("-date", "project__name", "-creation_date")
        )
        context_data["daily_hours_sum"] = context_data["object_list"].order_by().get_work_hours_sum_for_all_dates()
        context_data["monthly_hours_sum"] = context_data["object_list"].order_by().get_work_hours_sum_for_all_authors()
        context_data["project_form"] = ProjectJoinForm(
            queryset=Project.objects.exclude(members__id=self.request.user.id).order_by("name")
        )
        context_data["hide_join"] = not Project.objects.exclude(members__id=self.request.user.id).exists()
        return context_data

    def form_valid_for_join_project(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid_for_join_project(self, form: ProjectJoinForm) -> HttpResponse:
        return self.render_to_response(context={"form": form})

    def form_valid(self, form: ReportForm) -> ReportForm:
        self.object = form.save(commit=False)  # pylint: disable=attribute-defined-outside-init
        self.object.author = self.request.user
        return super(ReportCreateView, self).form_valid(form)

    def get_success_url(self) -> HttpResponseRedirect:
        return reverse("custom-report-list")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(
        allowed_user_types=[
            CustomUser.UserType.EMPLOYEE.name,
            CustomUser.UserType.MANAGER.name,
            CustomUser.UserType.ADMIN.name,
        ]
    ),
    name="dispatch",
)
class ReportDetailView(UserIsManagerOfCurrentReportProjectMixin, UserIsAuthorOfCurrentReportMixin, UpdateView):
    template_name = "employees/report_detail.html"
    form_class = ReportForm
    model = Report

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = ReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("custom-report-list")

    def form_valid(self, form: ReportForm) -> HttpResponseRedirectBase:
        instance = form.save(commit=False)
        instance.editable = True
        instance.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.object.author
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(
        allowed_user_types=[
            CustomUser.UserType.EMPLOYEE.name,
            CustomUser.UserType.MANAGER.name,
            CustomUser.UserType.ADMIN.name,
        ]
    ),
    name="dispatch",
)
class ReportDeleteView(UserIsAuthorOfCurrentReportMixin, UserIsManagerOfCurrentReportProjectMixin, DeleteView):
    model = Report

    def get_success_url(self) -> str:
        logger.debug(f"Report with id: {self.kwargs['pk']} has been deleted")
        return reverse("custom-report-list")


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class AuthorReportView(DetailView):
    template_name = "employees/author_report_list.html"
    model = CustomUser
    queryset = CustomUser.objects.prefetch_related("report_set")

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["UI_text"] = AuthorReportListStrings
        context["daily_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_dates()
        context["monthly_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_authors()
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class AdminReportView(UpdateView):
    template_name = "employees/admin_report_detail.html"
    form_class = ReportForm
    model = Report

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = AdminReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("author-report-list", kwargs={"pk": self.object.author.id})

    def form_valid(self, form: ReportForm) -> HttpResponseRedirectBase:
        self.object = form.save(commit=False)  # pylint: disable=attribute-defined-outside-init
        self.object.editable = True
        self.object.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.object.author
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.MANAGER.name, CustomUser.UserType.ADMIN.name]),
    name="dispatch",
)
class ProjectReportList(UserIsManagerOfCurrentProjectMixin, DetailView):
    template_name = "employees/project_report_list.html"
    model = Project
    queryset = Project.objects.prefetch_related("report_set")

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["UI_text"] = ProjectReportListStrings
        context["monthly_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_authors()
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.MANAGER.name, CustomUser.UserType.ADMIN.name]),
    name="dispatch",
)
class ProjectReportDetail(UserIsManagerOfCurrentReportProjectMixin, UpdateView):
    template_name = "employees/project_report_detail.html"
    form_class = ReportForm
    model = Report

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = ProjectReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("project-report-list", kwargs={"pk": self.object.project.id})

    def form_valid(self, form: ReportForm) -> HttpResponseRedirectBase:
        self.object = form.save(commit=False)  # pylint: disable=attribute-defined-outside-init
        self.object.editable = True
        self.object.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.object.author
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class ExportUserReportView(DetailView):
    model = CustomUser

    def render_to_response(self, context: dict, **response_kwargs: Any) -> HttpResponse:
        author = super().get_object()
        response = HttpResponse(content_type=ExcelGeneratorSettingsConstants.CONTENT_TYPE_FORMAT.value)
        response["Content-Disposition"] = ExcelGeneratorSettingsConstants.EXPORTED_FILE_NAME.value.format(
            author.email, datetime.date.today()
        )
        work_book = generate_xlsx_for_single_user(author)
        work_book.save(response)
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class ExportReportsInProjectView(UserIsManagerOfCurrentProjectMixin, DetailView):
    model = Project

    def render_to_response(self, context: dict, **response_kwargs: Any) -> HttpResponse:
        project = super().get_object()
        response = HttpResponse(content_type=ExcelGeneratorSettingsConstants.CONTENT_TYPE_FORMAT.value)
        response["Content-Disposition"] = ExcelGeneratorSettingsConstants.EXPORTED_FILE_NAME.value.format(
            project.name, datetime.date.today()
        )
        work_book = generate_xlsx_for_project(project)
        work_book.save(response)
        return response
