import datetime

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from employees.common.strings import ProjectReportListStrings
from employees.factories import ReportFactory
from employees.models import Report
from employees.models import TaskActivityType
from employees.views import ProjectReportList
from employees.views import ReportViewSet
from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import AdminUserFactory
from users.models import CustomUser


class DataSetUpToTests(TestCase):
    def setUp(self):
        task_type = TaskActivityType(pk=1, name="Other")
        task_type.full_clean()
        task_type.save()
        self.user = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()

        self.report = Report(
            date=datetime.datetime.now().date(),
            description="Some description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        self.report.full_clean()
        self.report.save()


class ReportListTests(DataSetUpToTests):
    def test_report_list_view_should_display_users_report_list_on_get(self):
        request = APIRequestFactory().get(path=reverse("report-list"))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_report_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        request = APIRequestFactory().get(path=reverse("report-list"))
        request.user = AnonymousUser()
        response = ReportViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 403)

    def test_report_list_view_should_not_display_other_users_reports(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it", password="otheruserpasswd", first_name="Jane", last_name="Doe", country="PL"
        )
        other_user.full_clean()
        other_user.save()

        other_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=other_user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
            task_activities=TaskActivityType.objects.get(name="Other"),
        )
        other_report.full_clean()
        other_report.save()

        request = APIRequestFactory().get(path=reverse("report-list"))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_report_list_view_should_add_new_report_on_post(self):
        request = APIRequestFactory().post(
            path=reverse("report-list"),
            data={
                "date": datetime.datetime.now().date(),
                "description": "Some description",
                "project": self.project,
                "work_hours": "8:00",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.all().count(), 2)


class ReportDetailTests(DataSetUpToTests):
    def test_report_detail_view_should_display_report_details_on_get(self):
        request = APIRequestFactory().get(path=reverse("report-detail", args=(self.report.pk,)))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "retrieve"})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_report_list_view_should_not_be_accessible_for_unauthenticated_users(self):
        request = APIRequestFactory().get(path=reverse("report-detail", args=(self.report.pk,)))
        request.user = AnonymousUser()
        response = ReportViewSet.as_view({"get": "retrieve"})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 403)

    def test_report_detail_view_should_not_render_non_existing_report_on_get(self):
        request = APIRequestFactory().get(path=reverse("report-detail", args=(999,)))
        request.user = self.user
        response = ReportViewSet.as_view({"get": "retrieve"})(request, pk=999)
        self.assertEqual(response.status_code, 404)

    def test_report_detail_view_should_update_report_on_put(self):
        new_description = "Some other description"
        request = APIRequestFactory().put(
            path=reverse("report-detail", args=(self.report.pk,)),
            data={
                "date": datetime.datetime.now().date(),
                "description": new_description,
                "project": self.project,
                "work_hours": "8:00",
                "task_activities": TaskActivityType.objects.get(name="Other"),
            },
        )
        request.user = self.user
        response = ReportViewSet.as_view({"put": "update"})(request, pk=self.report.pk)
        current_description = Report.objects.get(pk=self.report.pk).description
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_description, new_description)

    def test_report_detail_view_should_delete_report_on_delete(self):
        request = APIRequestFactory().delete(path=reverse("report-detail", args=(self.report.pk,)))
        request.user = self.user
        response = ReportViewSet.as_view({"delete": "destroy"})(request, pk=self.report.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Report.objects.all().count(), 0)


class ProjectReportListTests(TestCase):
    def _assert_response_contain_report(self, response, reports):
        for report in reports:
            dates = ["creation_date", "last_update"]
            other_fields = ["description", "author", "task_activities"]
            work_hours = report.work_hours_str
            fields_to_check = [work_hours]
            for date in dates:
                fields_to_check.append(
                    datetime.datetime.strftime(
                        datetime.datetime.fromtimestamp(int(getattr(report, date).timestamp())), "%B %-d, %Y, %-I:%M"
                    )
                )
            for field in other_fields:
                if field == "author":
                    fields_to_check.append(getattr(report, field).email)
                else:
                    fields_to_check.append(getattr(report, field))
            for field in fields_to_check:
                self.assertContains(response, field)

    def setUp(self):
        super().setUp()
        self.task_type = TaskActivityType(pk=1, name="Other")
        self.task_type.full_clean()
        self.task_type.save()
        self.user = AdminUserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project)
        self.data = {
            "date": timezone.now().date(),
            "description": "Some other description",
            "project": self.report.project.pk,
            "author": self.user.pk,
            "task_activities": self.report.task_activities.pk,
            "work_hours": "8.00",
        }
        self.url = reverse("project-report-list", kwargs={"pk": self.project.pk})

    def test_project_report_list_view_should_display_projects_report_list_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ProjectReportList.template_name)
        self.assertContains(response, self.project.name)
        self._assert_response_contain_report(response, [self.report])

    def test_project_report_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_project_report_list_view_should_not_display_non_existing_projects_reports(self):
        response = self.client.get(reverse("project-report-list", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)

    def test_project_report_list_view_should_not_display_other_projects_reports(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()

        other_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=self.user,
            project=other_project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_report.full_clean()
        other_report.save()

        request = APIRequestFactory().get(path=reverse("project-report-list", args=(self.project.pk,)))
        request.user = self.user
        response = ProjectReportList.as_view()(request, pk=self.project.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_report.description)

    def test_project_report_list_view_should_display_message_if_project_has_no_reports(self):
        other_project = Project(name="Other Project", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        response = self.client.get(reverse("project-report-list", kwargs={"pk": other_project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ProjectReportListStrings.NO_REPORTS_MESSAGE.value)

    def test_that_project_report_list_should_return_list_of_all_reports_assigned_to_project(self):
        other_user = CustomUser(
            email="otheruser@codepoets.it", password="otheruserpasswd", first_name="Jane", last_name="Doe", country="PL"
        )
        other_user.full_clean()
        other_user.save()
        self.project.members.add(other_user)

        other_project = Project(name="Project test", start_date=datetime.datetime.now())
        other_project.full_clean()
        other_project.save()
        other_project.members.add(self.user)
        other_project.members.add(other_user)

        other_project_report = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=self.user,
            project=other_project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_project_report.full_clean()
        other_project_report.save()

        other_report_1 = Report(
            date=datetime.datetime.now().date(),
            description="Some other description",
            author=other_user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_report_1.full_clean()
        other_report_1.save()

        other_report_2 = Report(
            date=datetime.date(2001, 1, 1),
            description="Some other description",
            author=self.user,
            project=self.project,
            work_hours=datetime.timedelta(hours=8),
        )
        other_report_2.full_clean()
        other_report_2.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ProjectReportList.template_name)
        self.assertContains(response, self.project.name)
        self._assert_response_contain_report(response, [self.report, other_report_1, other_report_2])
