from django.core import management
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone
from parameterized import parameterized

from employees.models import Report
from managers.models import Project
from sheetstorm.management.commands.constants import DATA_SIZE_PARAMETER
from sheetstorm.management.commands.constants import SMALL_SET
from sheetstorm.management.commands.constants import SUPERUSER_USER_TYPE
from sheetstorm.management.commands.constants import DataSize
from sheetstorm.management.commands.constants import ProjectType
from sheetstorm.management.commands.constants import UsersInProjects
from sheetstorm.management.commands.generate_test_data import Command as GenerateTestDataCommand
from users.factories import UserFactory
from users.models import CustomUser


class CreateUsersTests(TestCase):
    def test_that_command_should_create_superuser_when_superuser_is_requested(self):
        management.call_command("generate_test_data", SUPERUSER=True)

        self.assertTrue(CustomUser.objects.filter(is_superuser=True).exists())

    def test_that_command_should_not_create_superuser_when_superuser_is_not_requested(self):
        management.call_command("generate_test_data")

        self.assertFalse(CustomUser.objects.filter(is_superuser=True).exists())

    def test_that_command_should_not_create_superuser_when_superuser_is_requested_but_already_exists(self):
        UserFactory(is_superuser=True)

        management.call_command("generate_test_data", SUPERUSER=True)

        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 1)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 3),
            (CustomUser.UserType.EMPLOYEE.name, 5),
            (CustomUser.UserType.MANAGER.name, 4),
        ]
    )
    def test_that_result_of_command_should_be_specified_number_of_users_in_database(
        self, user_type, number_of_users_to_create
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users_to_create})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users_to_create)

    def test_that_command_should_not_create_any_user_when_any_argument_is_not_specified(self):
        management.call_command("generate_test_data")

        self.assertEqual(CustomUser.objects.all().count(), 0)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 2),
            (CustomUser.UserType.EMPLOYEE.name, 2),
            (CustomUser.UserType.MANAGER.name, 2),
        ]
    )
    def test_that_command_should_not_require_all_arguments_to_create_specified_users(
        self, user_type, number_of_users_to_create
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users_to_create})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users_to_create)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 0, 0),
            (CustomUser.UserType.ADMIN.name, -100, 0),
            (CustomUser.UserType.ADMIN.name, 2, 2),
            (CustomUser.UserType.EMPLOYEE.name, 0, 0),
            (CustomUser.UserType.EMPLOYEE.name, -100, 0),
            (CustomUser.UserType.EMPLOYEE.name, 2, 2),
            (CustomUser.UserType.MANAGER.name, 0, 0),
            (CustomUser.UserType.MANAGER.name, -100, 0),
            (CustomUser.UserType.MANAGER.name, 2, 2),
        ]
    )
    def test_that_command_should_not_create_users_when_specified_number_is_not_greater_than_0(
        self, user_type, number_of_users_to_create, expected_number_of_users_in_database
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users_to_create})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), expected_number_of_users_in_database)

    @parameterized.expand(
        [
            (CustomUser.UserType.ADMIN.name, 1),
            (CustomUser.UserType.EMPLOYEE.name, 1),
            (CustomUser.UserType.MANAGER.name, 1),
        ]
    )
    def test_that_despite_filled_database_command_should_create_specified_number_of_users(
        self, user_type, number_of_users
    ):
        management.call_command("generate_test_data", **{user_type: number_of_users})

        management.call_command("generate_test_data", **{user_type: number_of_users + 1})

        self.assertEqual(CustomUser.objects.filter(user_type=user_type).count(), number_of_users + 1)


class CreateProjectsTests(TestCase):
    def test_that_result_of_command_should_be_specified_number_of_projects_in_database(self):
        number_of_projects_to_create = {
            ProjectType.SUSPENDED.name: 4,
            ProjectType.ACTIVE.name: 3,
            ProjectType.COMPLETED.name: 2,
        }

        management.call_command("generate_test_data", **number_of_projects_to_create)

        self.assertEqual(
            Project.objects.filter_suspended().count(), number_of_projects_to_create[ProjectType.SUSPENDED.name]
        )
        self.assertEqual(Project.objects.filter_active().count(), number_of_projects_to_create[ProjectType.ACTIVE.name])
        self.assertEqual(
            Project.objects.filter_completed().count(), number_of_projects_to_create[ProjectType.COMPLETED.name]
        )

    def test_that_command_should_not_create_any_project_when_any_argument_is_not_specified(self):
        management.call_command("generate_test_data")

        self.assertEqual(Project.objects.all().count(), 0)

    @parameterized.expand(
        [(ProjectType.SUSPENDED.name, 2), (ProjectType.ACTIVE.name, 2), (ProjectType.COMPLETED.name, 2)]
    )
    def test_that_command_should_not_require_all_arguments_to_create_specified_projects(
        self, project_type, number_of_projects_to_create
    ):
        management.call_command("generate_test_data", **{project_type: number_of_projects_to_create})

        self.check_number_of_projects_in_database(project_type, number_of_projects_to_create)

    @parameterized.expand(
        [
            (ProjectType.SUSPENDED.name, 0, 0),
            (ProjectType.SUSPENDED.name, -100, 0),
            (ProjectType.SUSPENDED.name, 2, 2),
            (ProjectType.ACTIVE.name, 0, 0),
            (ProjectType.ACTIVE.name, -100, 0),
            (ProjectType.ACTIVE.name, 2, 2),
            (ProjectType.COMPLETED.name, 0, 0),
            (ProjectType.COMPLETED.name, -100, 0),
            (ProjectType.COMPLETED.name, 2, 2),
        ]
    )
    def test_that_command_should_not_create_projects_when_specified_number_is_not_greater_than_0(
        self, project_type, number_of_projects_to_create, expected_number_of_projects_in_database
    ):
        management.call_command("generate_test_data", **{project_type: number_of_projects_to_create})

        self.check_number_of_projects_in_database(project_type, expected_number_of_projects_in_database)

    @parameterized.expand(
        [(ProjectType.SUSPENDED.name, 1), (ProjectType.ACTIVE.name, 1), (ProjectType.COMPLETED.name, 1)]
    )
    def test_that_despite_filled_database_command_should_create_specified_number_of_projects(
        self, project_type, number_of_projects
    ):
        management.call_command("generate_test_data", **{project_type: number_of_projects})

        management.call_command("generate_test_data", **{project_type: number_of_projects + 1})

        self.check_number_of_projects_in_database(project_type, number_of_projects + 1)

    def check_number_of_projects_in_database(self, project_type, expected_number_of_projects):
        if project_type == ProjectType.SUSPENDED.name:
            self.assertEqual(Project.objects.filter_suspended().count(), expected_number_of_projects)
        elif project_type == ProjectType.ACTIVE.name:
            self.assertEqual(Project.objects.filter_active().count(), expected_number_of_projects)
        elif project_type == ProjectType.COMPLETED.name:
            self.assertEqual(Project.objects.filter_completed().count(), expected_number_of_projects)


class CombinedOptionsTests(TestCase):
    def setUp(self):
        self.number_of_admins_to_create = 1
        self.number_of_employees_to_create = 2
        self.number_of_managers_to_create = 2

        self.number_of_suspended_projects_to_create = 1
        self.number_of_active_projects_to_create = 2
        self.number_of_completed_projects_to_create = 2

        self.combined_options = {
            CustomUser.UserType.ADMIN.name: self.number_of_admins_to_create,
            CustomUser.UserType.EMPLOYEE.name: self.number_of_employees_to_create,
            CustomUser.UserType.MANAGER.name: self.number_of_managers_to_create,
            SUPERUSER_USER_TYPE: True,
            ProjectType.SUSPENDED.name: self.number_of_suspended_projects_to_create,
            ProjectType.ACTIVE.name: self.number_of_active_projects_to_create,
            ProjectType.COMPLETED.name: self.number_of_completed_projects_to_create,
        }

    def test_that_passing_users_arguments_should_not_affect_creating_projects(self):
        management.call_command("generate_test_data", **self.combined_options)

        self.check_number_of_all_projects_in_database()

    def test_that_passing_projects_arguments_should_not_affect_creating_users(self):
        management.call_command("generate_test_data", **self.combined_options)

        self.check_number_of_all_users_in_database()

    def test_that_result_of_passing_all_arguments_should_be_created_specified_number_of_projects_and_users(self):
        management.call_command("generate_test_data", **self.combined_options)

        self.check_number_of_all_projects_in_database()

        self.check_number_of_all_users_in_database()

    def check_number_of_all_projects_in_database(self):
        self.assertEqual(Project.objects.filter_suspended().count(), self.number_of_suspended_projects_to_create)
        self.assertEqual(Project.objects.filter_active().count(), self.number_of_active_projects_to_create)
        self.assertEqual(Project.objects.filter_completed().count(), self.number_of_completed_projects_to_create)

    def check_number_of_all_users_in_database(self):
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.ADMIN.name, is_superuser=False).count(),
            self.number_of_admins_to_create,
        )
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.EMPLOYEE.name).count(),
            self.number_of_employees_to_create,
        )
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.MANAGER.name).count(),
            self.number_of_managers_to_create,
        )
        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 1)


class PassIncorrectArgumentsTests(TestCase):
    @parameterized.expand([("--admin", "test-text"), ("--employee", "test-text"), ("--manager", "test-text")])
    def test_that_passing_text_instead_of_number_for_users_arguments_should_raise_error(self, user_type, test_text):
        with self.assertRaises(CommandError):
            management.call_command("generate_test_data", f"{user_type}={test_text}")

    @parameterized.expand([("--suspended", "test-text"), ("--active", "test-text"), ("--completed", "test-text")])
    def test_that_passing_text_instead_of_number_for_projects_arguments_should_raise_error(
        self, project_type, test_text
    ):
        with self.assertRaises(CommandError):
            management.call_command("generate_test_data", f"{project_type}={test_text}")

    @parameterized.expand([(1,), ("test_text",)])
    def test_that_passing_any_value_for_positional_superuser_argument_should_raise_error(self, test_value):
        with self.assertRaises(CommandError):
            management.call_command("generate_test_data", f"--superuser={test_value}")

    @parameterized.expand([(1,), ("test_text",)])
    def test_that_passing_any_value_for_data_size_parameter_other_than_defined_sizes_should_raise_error(
        self, test_value
    ):
        with self.assertRaises(CommandError):
            management.call_command("generate_test_data", f"--data-size={test_value}")


class CreateDataFromPreparedSetTests(TestCase):
    def test_that_command_should_create_specified_set_when_there_is_request(self):
        management.call_command("generate_test_data", "--data-size=small")

        self.compare_quantity_in_database_with_small_set()

    def test_that_result_of_passing_all_arguments_when_prepared_set_is_requested_should_be_created_specified_set(self):
        combined_options = {
            CustomUser.UserType.ADMIN.name: 100,
            CustomUser.UserType.EMPLOYEE.name: 2,
            CustomUser.UserType.MANAGER.name: None,
            SUPERUSER_USER_TYPE: False,
            ProjectType.SUSPENDED.name: 100,
            ProjectType.ACTIVE.name: 1,
            ProjectType.COMPLETED.name: None,
            DATA_SIZE_PARAMETER: DataSize.SMALL.value,
        }

        management.call_command("generate_test_data", **combined_options)

        self.compare_quantity_in_database_with_small_set()

    def compare_quantity_in_database_with_small_set(self):
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.ADMIN.name, is_superuser=False).count(),
            SMALL_SET[CustomUser.UserType.ADMIN.name],
        )
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.MANAGER.name, is_superuser=False).count(),
            SMALL_SET[CustomUser.UserType.MANAGER.name],
        )
        self.assertEqual(
            CustomUser.objects.filter(user_type=CustomUser.UserType.EMPLOYEE.name, is_superuser=False).count(),
            SMALL_SET[CustomUser.UserType.EMPLOYEE.name],
        )

        self.assertEqual(Project.objects.filter_active().count(), SMALL_SET[ProjectType.ACTIVE.name])
        self.assertEqual(Project.objects.filter_suspended().count(), SMALL_SET[ProjectType.SUSPENDED.name])
        self.assertEqual(Project.objects.filter_completed().count(), SMALL_SET[ProjectType.COMPLETED.name])


class AddUsersToProjectsTests(TestCase):
    def setUp(self) -> None:
        management.call_command("generate_test_data", "--data-size=small")

    def test_that_number_of_added_users_to_project_should_be_less_or_equal_to_specified_max_number_in_prepared_set(
        self
    ):
        test_project_suspended = Project.objects.filter_suspended().first()
        test_project_completed = Project.objects.filter_completed().first()
        test_project_active = Project.objects.filter_active().first()

        max_number_of_users_in_suspended = (
            SMALL_SET[UsersInProjects.EMPLOYEE_SUSPENDED.name]
            + SMALL_SET[UsersInProjects.ADMIN_SUSPENDED.name]
            + SMALL_SET[UsersInProjects.MANAGER_SUSPENDED.name]
        )

        max_number_of_users_in_completed = (
            SMALL_SET[UsersInProjects.EMPLOYEE_COMPLETED.name]
            + SMALL_SET[UsersInProjects.ADMIN_COMPLETED.name]
            + SMALL_SET[UsersInProjects.MANAGER_COMPLETED.name]
        )

        max_number_of_users_in_active = (
            SMALL_SET[UsersInProjects.EMPLOYEE_ACTIVE.name]
            + SMALL_SET[UsersInProjects.ADMIN_ACTIVE.name]
            + SMALL_SET[UsersInProjects.MANAGER_ACTIVE.name]
        )

        self.assertLessEqual(test_project_suspended.members.count(), max_number_of_users_in_suspended)
        self.assertLessEqual(test_project_completed.members.count(), max_number_of_users_in_completed)
        self.assertLessEqual(test_project_active.members.count(), max_number_of_users_in_active)

    def test_that_number_of_added_managers_to_project_should_be_less_or_equal_to_specified_max_number_in_prepared_set(
        self
    ):
        test_project_suspended = Project.objects.filter_suspended().first()
        test_project_completed = Project.objects.filter_completed().first()
        test_project_active = Project.objects.filter_active().first()

        self.assertLessEqual(test_project_suspended.managers.count(), SMALL_SET[UsersInProjects.MANAGER_SUSPENDED.name])
        self.assertLessEqual(test_project_completed.managers.count(), SMALL_SET[UsersInProjects.MANAGER_COMPLETED.name])
        self.assertLessEqual(test_project_active.managers.count(), SMALL_SET[UsersInProjects.MANAGER_ACTIVE.name])


class CreateUserReportsTests(TestCase):
    def setUp(self) -> None:
        management.call_command("generate_test_data", "--data-size=small")

    def test_that_user_should_have_at_least_number_of_reports_equal_to_number_of_days_project_lasts_minus_one_day(self):
        management.call_command("generate_test_data", "--data-size=small")

        number_of_possible_days_with_reports = self.get_number_of_possible_days_with_reports()

        user = self.get_user_that_is_member_of_any_project()

        self.assertGreaterEqual(Report.objects.filter(author=user).count(), number_of_possible_days_with_reports)

    def test_that_command_should_not_create_new_reports_if_the_database_already_contains_reports(self):
        expected_number_of_reports_in_database = Report.objects.count()

        management.call_command("generate_test_data", "--data-size=small")

        self.assertEqual(Report.objects.count(), expected_number_of_reports_in_database)

    @staticmethod
    def get_user_that_is_member_of_any_project():
        for user in CustomUser.objects.all():
            if user.projects.count() > 0:
                return user

        return None

    @staticmethod
    def get_number_of_possible_days_with_reports():
        project_start_date = timezone.now() - GenerateTestDataCommand.PROJECT_START_DATE_TIME_DELTA
        project_stop_date = timezone.now() - GenerateTestDataCommand.PROJECT_STOP_DATE_TIME_DELTA

        number_of_days_of_project_duration = (project_stop_date - project_start_date).days

        return number_of_days_of_project_duration - 1
