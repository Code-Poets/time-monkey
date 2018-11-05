from django.test import TestCase
from managers.commons.constants import *
from managers.models import Project
from django.core.exceptions import ValidationError
from django.utils import timezone


class TestProjectModel(TestCase):
    def test_that_project_should_have_start_date(self):
        project = Project(
            name='X',
        )
        with self.assertRaisesRegexp(
            ValidationError,
            "This field cannot be null.",
        ):
            project.full_clean()

    def test_that_project_name_should_not_be_blank(self):
        project = Project(
            start_date=timezone.now(),
        )
        with self.assertRaisesRegexp(
                ValidationError,
                "This field cannot be blank.",
        ):
            project.full_clean()

    def test_that_project_name_should_not_be_longer_than_MAX_NAME_LENGTH(self):
        project = Project(
            start_date=timezone.now(),
            name='X'*(MAX_NAME_LENGTH+1),
        )
        with self.assertRaisesRegexp(
            ValidationError,
            "Ensure this value has at most " + str(MAX_NAME_LENGTH) + " characters",
        ):
            project.full_clean()

    def test_that_project_name_should_be_longer_than_MAX_NAME_LENGTH(self):
        project = Project(
            start_date=timezone.now(),
            name='X'*MAX_NAME_LENGTH,
        )
        try:
            project.full_clean()
        except ValidationError:
            self.fail("Ensure this value has at most " + str(MAX_NAME_LENGTH) + " characters")