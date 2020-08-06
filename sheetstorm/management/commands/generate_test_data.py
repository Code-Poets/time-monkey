import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from managers.factories import ProjectFactory
from managers.models import Project
from users.factories import UserFactory

CustomUser = get_user_model()

superuser_user_type = "SUPERUSER"

suspended_project = "suspended"
active_project = "active"
completed_project = "completed"


class Command(BaseCommand):
    help = "Create initial sample data for SheetStorm application testing."

    @transaction.atomic
    def handle(self, *args, **options):
        user_options = self._get_user_options(options)
        is_need_to_create_superuser = self._get_superuser_request(options)

        for (user_type, number_of_users) in user_options.items():
            if number_of_users is not None:
                self.create_user(user_type, number_of_users)

        if is_need_to_create_superuser:
            self.create_user(superuser_user_type)

        project_options = self._get_project_options(options)

        for (project_type, number_of_projects) in project_options.items():
            self.create_project(project_type, number_of_projects)

        logging.info(f"Total number of users in the database: {CustomUser.objects.count()}")
        logging.info(f"Total number of projects in the database: {Project.objects.count()}")

    @staticmethod
    def _get_user_options(options):
        return {
            CustomUser.UserType.ADMIN.name: options[CustomUser.UserType.ADMIN.name],
            CustomUser.UserType.EMPLOYEE.name: options[CustomUser.UserType.EMPLOYEE.name],
            CustomUser.UserType.MANAGER.name: options[CustomUser.UserType.MANAGER.name],
        }

    @staticmethod
    def _get_superuser_request(options):
        is_superuser_create_request = options[superuser_user_type]
        is_superuser_in_database = CustomUser.objects.filter(is_superuser=True).exists()

        return is_superuser_create_request and not is_superuser_in_database

    def create_user(self, user_type, number_of_users_to_create=1):
        factory_parameters = self._set_user_factory_parameters(user_type)

        for user_number in range(number_of_users_to_create):
            user_email = f"user.{user_type}{user_number + 1}@codepoets.it".lower()

            if not CustomUser.objects.filter(email=user_email).exists():
                logging.info(f"{number_of_users_to_create - user_number} {user_type}(s) left to create")
                UserFactory(**factory_parameters, email=user_email)

    @staticmethod
    def _set_user_factory_parameters(user_type):
        return {
            "user_type": CustomUser.UserType.ADMIN.name if user_type == superuser_user_type else user_type,
            "is_staff": user_type in (CustomUser.UserType.ADMIN.name, superuser_user_type),
            "is_superuser": user_type == superuser_user_type,
        }

    @staticmethod
    def _get_project_options(options):
        return {
            suspended_project: options[suspended_project] - Project.objects.filter_suspended().count()
            if options[suspended_project] is not None
            else 0,
            active_project: options[active_project] - Project.objects.filter_active().count()
            if options[active_project] is not None
            else 0,
            completed_project: options[completed_project] - Project.objects.filter_completed().count()
            if options[completed_project] is not None
            else 0,
        }

    def create_project(self, project_type, number_of_projects_to_create):
        factory_parameters = self._set_project_factory_parameters(project_type)

        for project_number in range(number_of_projects_to_create):
            logging.info(f"{number_of_projects_to_create - project_number} {project_type} project(s) left to create")
            ProjectFactory(**factory_parameters)

    def _set_project_factory_parameters(self, project_type):
        return {
            "start_date": self._set_project_start_date(timezone.now()),
            "suspended": project_type == suspended_project,
            "stop_date": self._set_project_stop_date(timezone.now()) if project_type == completed_project else None,
        }

    @staticmethod
    def _set_project_start_date(date):
        return (
            date.replace(day=1, month=12, year=date.year - 1)
            if date.month == 1
            else date.replace(day=1, month=date.month - 1)
        )

    @staticmethod
    def _set_project_stop_date(date):
        return date - timezone.timedelta(days=14)

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--admin",
            dest=CustomUser.UserType.ADMIN.name,
            type=int,
            help="Indicates the maximum number of admins to be in the database",
        )
        parser.add_argument(
            "-e",
            "--employee",
            dest=CustomUser.UserType.EMPLOYEE.name,
            type=int,
            help="Indicates the maximum number of employees to be in the database",
        )
        parser.add_argument(
            "-m",
            "--manager",
            dest=CustomUser.UserType.MANAGER.name,
            type=int,
            help="Indicates the maximum number of managers to be in the database",
        )
        parser.add_argument(
            "-s",
            "--superuser",
            dest=superuser_user_type,
            action="store_true",
            help="Create and add superuser to the database if not exist",
        )
        parser.add_argument(
            "-su",
            "--suspended",
            dest=suspended_project,
            type=int,
            help="Indicates the maximum number of suspended projects to be in the database",
        )
        parser.add_argument(
            "-ac",
            "--active",
            dest=active_project,
            type=int,
            help="Indicates the maximum number of active projects to be in the database",
        )
        parser.add_argument(
            "-co",
            "--completed",
            dest=completed_project,
            type=int,
            help="Indicates the maximum number of completed projects to be in the database",
        )
