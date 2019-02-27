import datetime

from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from django.test import TestCase

from users.models import CustomUser
from managers import views
from managers.models import Project


class ProjectTest(TestCase):
    def setUp(self):
        self.user = CustomUser(
            email="testuser@codepoets.it",
            first_name='John',
            last_name='Doe',
            country='PL',
            user_type=CustomUser.UserType.ADMIN.name,
        )
        self.user.password = 'newuserpasswd'
        self.user.set_password(self.user.password)
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
        self.project.managers.add(self.user)
        self.project.members.add(self.user)
        self.url = [
            reverse('custom-projects-list'),
            reverse('custom-project-create'),
            reverse('custom-project-detail', args=(self.project.pk,)),
            reverse('custom-project-update', args=(self.project.pk,)),
            reverse('custom-project-delete', args=(self.project.pk,)),
        ]


class ProjectsListTests(ProjectTest):
    def test_project_list_view_should_display_projects_list_on_get(self):
        request = APIRequestFactory().get(path=self.url[0])
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        projects_list = response.data['projects_queryset']
        self.assertTrue(self.project in projects_list)

    def test_projects_list_view_should_show_for_managers_only_own_projects(self):
        self.user.user_type = CustomUser.UserType.MANAGER.name
        manager_project_list = Project.objects.filter(managers__id=self.user.pk)
        request = APIRequestFactory().get(path=self.url[0])
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        projects_list = response.data['projects_queryset']
        self.assertEqual(list(manager_project_list), list(projects_list))

    def test_project_list_view_should_display_projects_sorted_by_name_ascending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=name')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('name' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_name_descending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=-name')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-name' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_start_date_ascending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=start_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('start_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_start_date_descending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=-start_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-start_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_stop_date_ascending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=stop_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('stop_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_stop_date_descending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=-stop_date')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-stop_date' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_members_count_ascending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=members_count')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('members_count' in projects_list.query.order_by)

    def test_project_list_view_should_display_projects_sorted_by_members_count_descending(self):
        request = APIRequestFactory().get(path=self.url[0] + '?sort=-members_count')
        request.user = self.user
        response = views.ProjectsList.as_view()(request)
        projects_list = response.data['projects_queryset']
        self.assertTrue(projects_list.ordered)
        self.assertTrue('-members_count' in projects_list.query.order_by)


class ProjectCreateTests(ProjectTest):
    def test_project_create_view_should_display_create_project_form_on_get(self):
        request = APIRequestFactory().get(path=self.url[1])
        request.user = self.user
        response = views.ProjectCreate.as_view()(request,)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create new project')

    def test_project_create_view_should_add_new_project_on_post(self):
        request = APIRequestFactory().post(
            path=self.url[1],
            data={
                'name': 'Another Example Project',
                'start_date': datetime.datetime.now().date() - datetime.timedelta(days=30),
                'terminated': False,
                'managers': [self.user.pk, ],
                'members': [self.user.pk, ],
            }
        )
        request.user = self.user
        response = views.ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/projects/')
        self.assertEqual(Project.objects.filter(name='Another Example Project').count(), 1)

    def test_project_create_view_should_not_add_new_project_on_post_if_data_is_invalid(self):
        request = APIRequestFactory().post(
            path=self.url[1],
            data={
                'start_date': datetime.datetime.now().date() - datetime.timedelta(days=30),
                'terminated': False,
                'managers': [self.user.pk, ],
                'members': [self.user.pk, ],
            }
        )
        request.user = self.user
        response = views.ProjectCreate.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data.get('errors'), None)
        self.assertTrue('name' in response.data.get('errors'))
        self.assertEqual(Project.objects.filter(name='Another Example Project').count(), 0)


class ProjectDetailTests(ProjectTest):
    def test_project_detail_view_should_display_project_details_on_get(self):
        request = APIRequestFactory().get(path=self.url[2])
        request.user = self.user
        response = views.ProjectDetail.as_view()(request, self.project.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        project = response.data['project']
        self.assertEqual(self.project, project)

    def test_project_detail_view_should_return_404_status_code_on_get_if_project_does_not_exist(self):
        request = APIRequestFactory().get(path=self.url[2])
        request.user = self.user
        response = views.ProjectDetail.as_view()(request, self.project.pk + 1)
        self.assertEqual(response.status_code, 404)


class ProjectUpdateTests(ProjectTest):
    def test_project_update_view_should_display_project_update_serializer_on_get(self):
        request = APIRequestFactory().get(path=self.url[3])
        request.user = self.user
        response = views.ProjectUpdate.as_view()(request, self.project.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)
        self.assertEqual(response.data['serializer'].instance, self.project)

    def test_project_update_view_should_return_404_status_code_on_get_if_project_does_not_exist(self):
        request = APIRequestFactory().get(path=self.url[3])
        request.user = self.user
        response = views.ProjectUpdate.as_view()(request, self.project.pk + 1)
        self.assertEqual(response.status_code, 404)

    def test_project_update_view_should_update_project_on_post(self):
        request = APIRequestFactory().post(
            path=self.url[3],
            data={
                'name': 'New Example Project Name',
                'start_date': self.project.start_date,
                'managers': [self.user.pk, ],
                'members': [self.user.pk, ],
            }
        )
        request.user = self.user
        response = views.ProjectUpdate.as_view()(request, self.project.pk)
        self.project.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual('New Example Project Name', self.project.name)

    def test_project_update_view_should_update_project_on_post_if_data_is_invalid(self):
        request = APIRequestFactory().post(
            path=self.url[3],
            data={
                'start_date': self.project.start_date,
                'managers': [self.user.pk, ],
                'members': [self.user.pk, ],
            }
        )
        request.user = self.user
        response = views.ProjectUpdate.as_view()(request, self.project.pk)
        self.project.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data.get('errors'), None)
        self.assertTrue('name' in response.data.get('errors'))
