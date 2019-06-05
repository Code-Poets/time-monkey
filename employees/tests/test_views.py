import datetime

from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone

from employees.common.strings import AuthorReportListStrings
from employees.common.strings import ReportListStrings
from employees.factories import ReportFactory
from employees.models import Report
from employees.models import TaskActivityType
from employees.views import AdminReportView
from employees.views import AuthorReportView
from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import AdminUserFactory
from users.factories import UserFactory


class InitTaskTypeTestCase(TestCase):
    def setUp(self):
        task_type = TaskActivityType(pk=1, name="Other")
        task_type.full_clean()
        task_type.save()


class AuthorReportViewTests(InitTaskTypeTestCase):
    def setUp(self):
        super().setUp()
        self.user = AdminUserFactory()
        self.client.force_login(self.user)
        self.url = reverse("author-report-list", kwargs={"pk": self.user.pk})

    def test_author_reports_view_should_display_users_report_list_on_get(self):
        report = ReportFactory(author=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertContains(response, report.project.name)

    def test_author_report_list_view_should_not_display_other_users_reports(self):
        report = ReportFactory()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertNotContains(response, report.project.name)

    def test_author_report_list_view_should_display_message_if_user_has_no_reports(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AuthorReportView.template_name)
        self.assertContains(response, AuthorReportListStrings.NO_REPORTS_MESSAGE.value)


class AdminReportViewTests(InitTaskTypeTestCase):
    def setUp(self):
        super().setUp()
        self.user = AdminUserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project)
        self.url = reverse("admin-report-detail", kwargs={"pk": self.report.pk})
        self.data = {
            "date": timezone.now().date(),
            "description": "Some other description",
            "project": self.report.project.pk,
            "author": self.user.pk,
            "task_activities": self.report.task_activities.pk,
            "work_hours": "8:00",
        }

    def test_admin_report_detail_view_should_display_report_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, AdminReportView.template_name)
        self.assertContains(response, self.report.project.name)

    def test_admin_report_detail_view_should_update_report_on_post(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertEqual(self.report.description, self.data["description"])
        self.assertEqual(self.report.author, self.user)
        self.assertTrue(self.report.editable)


class ProjectReportDetailTests(InitTaskTypeTestCase):
    def setUp(self):
        super().setUp()
        self.user = AdminUserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project)
        self.url = reverse("project-report-detail", args=(self.report.pk,))
        self.data = {
            "date": self.report.date,
            "description": self.report.description,
            "project": self.report.project.pk,
            "author": self.report.author.pk,
            "task_activities": self.report.task_activities.pk,
            "work_hours": self.report.work_hours_str,
        }

    def test_project_report_detail_view_should_display_report_details(self):
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        self.assertEqual(response.context_data["form"].instance, self.report)

    def test_project_report_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_project_report_detail_view_should_update_report_on_post(self):
        self.data["description"] = "Some other description"
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.description, self.data["description"])
        self.assertTrue(self.report.editable)

    def test_project_report_detail_view_should_not_update_report_on_post_if_form_is_invalid(self):
        self.data["description"] = ""
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data["form"]._errors)
        self.assertTrue(self.report.editable)


class ReportDetailViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.project = ProjectFactory()
        self.project.members.add(self.user)
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user, project=self.project)
        self.url = reverse("custom-report-detail", args=(self.report.pk,))
        self.data = {
            "date": self.report.date,
            "description": self.report.description,
            "project": self.report.project.pk,
            "author": self.report.author,
            "task_activities": self.report.task_activities.pk,
            "work_hours": self.report.work_hours_str,
        }

    def test_custom_report_detail_view_should_display_report_details_on_get(self):
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)

    def test_custom_report_list_view_should_not_be_accessible_for_unauthenticated_users(self):
        self.client.logout()
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_custom_report_detail_view_should_not_render_non_existing_report(self):
        response = self.client.get(path=reverse("custom-report-detail", args=(999,)))
        self.assertEqual(response.status_code, 404)

    def test_custom_report_detail_view_should_update_report_on_post(self):
        self.data["description"] = "Some other description"
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.report.description, self.data["description"])

    def test_custom_report_detail_view_should_not_update_report_on_post_if_form_is_invalid(self):
        old_description = self.data["description"]
        self.data["description"] = "Some other description"
        self.data["project"] = None
        response = self.client.post(path=self.url, data=self.data)
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data["form"].errors)
        self.assertEqual(old_description, self.report.description)

    def test_custom_report_detail_view_should_not_update_report_if_author_is_not_a_member_of_selected_project(self):
        other_project = ProjectFactory()
        old_description = self.data["description"]
        self.data["description"] = "Some other description"
        old_project = self.data["project"]
        self.data["project"] = other_project.pk
        response = self.client.post(path=self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context_data["form"].errors)
        self.assertEqual(old_project, self.report.project.pk)
        self.assertEqual(old_description, self.report.description)

    def test_custom_report_detail_view_project_field_should_not_display_projects_the_author_is_not_a_member_of(self):
        other_project = ProjectFactory()
        response = self.client.get(path=reverse("custom-report-detail", args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            (other_project.pk, other_project.name) not in response.context_data["form"].fields["project"].choices
        )


class ReportDeleteViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.report = ReportFactory(author=self.user)
        self.url = reverse("custom-report-delete", args=(self.report.pk,))

    def test_delete_report_view_should_delete_report_on_post(self):
        response = self.client.post(path=self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Report.objects.filter(pk=self.report.pk).exists())


class ReportCustomListTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

        self.project = ProjectFactory()
        self.project.members.add(self.user)

        self.report = ReportFactory(author=self.user, project=self.project)
        self.report.full_clean()
        self.report.save()
        self.url = reverse("custom-report-list")
        self.client.force_login(self.user)
        self.new_project = ProjectFactory()

    def test_custom_list_view_should_display_users_report_list_on_get(self):
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.report.description)
        reports = response.context_data["object_list"]
        self.assertTrue(self.report in reports)

    def test_custom_list_view_should_not_be_accessible_for_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, 302)

    def test_custom_list_view_should_not_display_other_users_reports(self):
        other_user = UserFactory()
        other_report = ReportFactory()
        other_report.full_clean()
        other_report.save()
        self.client.force_login(other_user)
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.report.description)

    def test_custom_report_list_view_should_add_new_report_on_post(self):
        response = self.client.post(
            path=self.url,
            data={
                "date": datetime.datetime.now().date(),
                "description": "Some description",
                "project": self.project.pk,
                "work_hours": "8:00",
                "task_activities": self.report.task_activities.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Report.objects.all().count(), 2)

    def test_custom_report_list_view_should_not_add_new_report_on_post_if_form_is_invalid(self):
        response = self.client.post(
            path=self.url, data={"description": "Some description", "project": self.project.pk, "work_hours": "8:00"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.all().count(), 1)
        self.assertIsNotNone(response.context_data["form"].errors)

    def test_get_queryset_method_should_return_queryset_containing_all_of_current_users_reports(self):
        other_user = UserFactory()
        other_project = ProjectFactory()
        other_project.members.add(other_user)
        other_user_report = ReportFactory(author=other_user, project=other_project)

        ReportFactory(author=self.user, project=self.project)
        ReportFactory(author=self.user, project=self.project)
        response = self.client.get(path=self.url)
        queryset = response.context_data["object_list"]
        self.assertEqual(len(queryset), 3)
        self.assertFalse(other_user_report in queryset)
        for report in self.user.projects.all():
            self.assertContains(response, report)

    def test_custom_report_list_add_project_method_should_register_current_user_as_project_member(self):
        self.new_project.members.add(self.user)
        self.assertTrue(self.user in self.new_project.members.all())

    def test_custom_report_list_view_should_add_user_to_project_selected_in_project_join_form_on_join(self):
        response = self.client.post(path=self.url, data={"projects": self.new_project.pk, "join": "join"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user in self.new_project.members.all())

    def test_custom_report_list_view_should_not_add_user_to_project_if_join_not_in_request(self):
        response = self.client.post(
            path=self.url,
            data={
                "date": datetime.datetime.now().date(),
                "description": "Some description",
                "project": self.project.pk,
                "work_hours": "8:00",
                "task_activities": self.report.task_activities.pk,
                "projects": self.new_project.pk,
            },
        )
        self.assertTrue(response.status_code, 302)
        self.assertIn(self.new_project, Project.objects.all())
        self.assertTrue(self.user not in self.new_project.members.all())

    def test_custom_report_list_view_should_handle_no_project_being_selected_in_project_form_on_post(self):
        response = self.client.post(path=self.url, data={"join": "join"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context_data["form"].errors)

    def test_custom_report_list_view_should_display_message_if_there_are_no_projects_available_to_join_to(self):
        self.new_project.members.add(self.user)
        response = self.client.get(path=self.url)
        self.assertContains(response, ReportListStrings.NO_PROJECTS_TO_JOIN.value)

    def test_create_report_view_project_field_queryset_should_contain_only_projects_user_is_assigned_to_after_failed_post(
        self
    ):
        response = self.client.post(
            path=self.url,
            data={
                "date": datetime.datetime.now().date(),
                "description": "Some description",
                "project": self.project.pk,
                "work_hours": "8:00",
            },
        )
        project_field_choices = response.context_data["form"].fields["project"].choices
        self.assertTrue((self.project.pk, self.project.name) in project_field_choices)
        self.assertTrue((self.new_project.pk, self.new_project.name) not in project_field_choices)

    def test_create_report_view_project_field_queryset_should_contain_only_projects_user_is_assigned_to_after_project_join(
        self
    ):
        new_project_1 = ProjectFactory()
        project_without_user = ProjectFactory()
        self.client.post(path=self.url, data={"projects": new_project_1.pk, "join": "join"})
        get_response = self.client.get(path=self.url)
        project_field_choices = get_response.context_data["form"].fields["project"].choices
        self.assertTrue((self.project.pk, self.project.name) in project_field_choices)
        self.assertTrue((new_project_1.pk, new_project_1.name) in project_field_choices)
        self.assertTrue((project_without_user.pk, project_without_user.name) not in project_field_choices)

    def test_create_report_view_project_field_queryset_should_contain_only_projects_user_is_assigned_to_after_failed_project_join(
        self
    ):
        new_project = ProjectFactory()
        post_response = self.client.post(path=self.url, data={"join": "join"})
        self.assertTrue(post_response.context_data["form"].errors is not None)
        get_response = self.client.get(path=self.url)
        project_field_choices = get_response.context_data["form"].fields["project"].choices
        self.assertTrue((new_project.pk, new_project.name) not in project_field_choices)
        self.assertTrue((self.project.pk, self.project.name) in project_field_choices)
