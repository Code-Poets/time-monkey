import datetime

from django.db.models import Q
from django.test import TestCase
from managers.models import Project
from managers.templatetags import custom_tags
from users.models import CustomUser


class tenRangeTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            first_name='John',
            last_name='Doe',
            country='PL'
        )
        self.user.full_clean()
        self.user.save()

        self.project = Project(
            name='Example Project',
            start_date=datetime.datetime.now().date() - datetime.timedelta(days=30),
            stop_date=datetime.datetime.now().date(),
            terminated=False,
        )
        self.project.full_clean()
        self.project.save()

    def test_sort_by_templatetag_should_return_projects_sorted_by_name(self):
        projects = Project.objects.all()
        valid_ascending_result = Project.objects.order_by('name')
        ascending_result = custom_tags.sort_by(projects, 'name')
        valid_descending_result = Project.objects.order_by('-name')
        descending_result = custom_tags.sort_by(projects, '-name')
        self.assertTrue(ascending_result.ordered)
        self.assertEqual(list(ascending_result), list(valid_ascending_result))
        self.assertTrue(descending_result.ordered)
        self.assertEqual(list(descending_result), list(valid_descending_result))

    def test_sort_by_templatetag_should_return_projects_sorted_by_start_date(self):
        projects = Project.objects.all()
        valid_ascending_result = Project.objects.order_by('start_date')
        ascending_result = custom_tags.sort_by(projects, 'start_date')
        valid_descending_result = Project.objects.order_by('-start_date')
        descending_result = custom_tags.sort_by(projects, '-start_date')
        self.assertTrue(ascending_result.ordered)
        self.assertEqual(list(ascending_result), list(valid_ascending_result))
        self.assertTrue(descending_result.ordered)
        self.assertEqual(list(descending_result), list(valid_descending_result))

    def test_sort_by_templatetag_should_return_projects_sorted_by_stop_date(self):
        projects = Project.objects.all()
        valid_ascending_result = Project.objects.order_by('stop_date')
        ascending_result = custom_tags.sort_by(projects, 'stop_date')
        valid_descending_result = Project.objects.order_by('-stop_date')
        descending_result = custom_tags.sort_by(projects, '-stop_date')
        self.assertTrue(ascending_result.ordered)
        self.assertEqual(list(ascending_result), list(valid_ascending_result))
        self.assertTrue(descending_result.ordered)
        self.assertEqual(list(descending_result), list(valid_descending_result))

    def test_filter_id_templatetag_should_return_only_project_with_given_id(self):
        projects = Project.objects.all()
        valid_result = Project.objects.filter(pk=self.project.pk)
        result = custom_tags.filter_id(projects, self.project.pk)
        self.assertEqual(result.count(), valid_result.count())
        self.assertEqual(list(result), list(valid_result))

    def test_filter_start_date_templatetag_should_return_only_projects_with_given_start_date(self):
        projects = Project.objects.all()
        valid_result = Project.objects.filter(start_date=datetime.datetime.now().date())
        result = custom_tags.filter_start_date(projects, datetime.datetime.now().date())
        self.assertEqual(result.count(), valid_result.count())
        self.assertEqual(list(result), list(valid_result))

    def test_filter_start_date_templatetag_should_return_only_projects_with_given_stop_date(self):
        projects = Project.objects.all()
        valid_result = Project.objects.filter(stop_date=datetime.datetime.now().date())
        result = custom_tags.filter_stop_date(projects, datetime.datetime.now().date())
        self.assertEqual(result.count(), valid_result.count())
        self.assertEqual(list(result), list(valid_result))

    def test_filter_terminated_templatetag_should_return_only_terminated_projects(self):
        projects = Project.objects.all()
        valid_result = Project.objects.filter(terminated=True, stop_date=None)
        result = custom_tags.filter_terminated(projects)
        self.assertQuerysetEqual(result, valid_result)
        self.assertEqual(result.count(), valid_result.count())

    def test_filter_active_templatetag_should_return_only_active_projects(self):
        projects = Project.objects.all()
        valid_result = Project.objects.filter(terminated=False, stop_date=None)
        result = custom_tags.filter_active(projects)
        self.assertQuerysetEqual(result, valid_result)
        self.assertEqual(result.count(), valid_result.count())

    def test_filter_completed_templatetag_should_return_only_ended_projects(self):
        projects = Project.objects.all()
        valid_result = Project.objects.filter(~Q(stop_date=None))
        result = custom_tags.filter_completed(projects)
        self.assertEqual(list(result), list(valid_result))
        self.assertEqual(result.count(), valid_result.count())
