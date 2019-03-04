from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory

from users.forms import LoginAuthentication
from users.models import CustomUser
from users.views import CustomUserLoginView


class TestCustomUserLogin(TestCase):
    def setUp(self):
        CustomUser.objects._create_user(
            "testuser@codepoets.it",
            "testuserpasswd",
            False,
            False,
            CustomUser.UserType.EMPLOYEE.name,
        )

    def test_user_client_should_log_in_with_correct_email_and_password(self):
        self.assertTrue(
            self.client.login(email="testuser@codepoets.it", password="testuserpasswd")
        )

    def test_user_client_should_not_log_in_with_wrong_email(self):
        self.assertFalse(
            self.client.login(email="wrongtestuser@codepoets.it", password="testuserpasswd")
        )

    def test_user_client_should_not_log_in_with_wrong_password(self):
        self.assertFalse(
            self.client.login(email="testuser@codepoets.it", password="wrongtestuserpasswd")
        )

    def test_user_client_should_not_log_in_when_email_is_none(self):
        self.assertFalse(
            self.client.login(email=None, password="wrongtestuserpasswd")
        )

    def test_user_client_should_not_log_in_when_password_is_none(self):
        self.assertFalse(
            self.client.login(email="testuser@codepoets.it", password=None)
        )


class TestLoginAuthentication(TestCase):
    def setUp(self):
        self.user = CustomUser.objects._create_user(
            "testuser@codepoets.it",
            "testuserpasswd",
            False,
            False,
            CustomUser.UserType.EMPLOYEE.name,
        )

    def test_user_should_log_in_without_domain(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'username': 'testuser',
                'password': 'testuserpasswd'
            }
        )
        self.assertEqual(302, response.status_code)
        self.assertEqual('/', response.url)

    def test_user_should_not_log_in_with_wrong_username(self):
        response = self.client.post(
            path=reverse('login'),
            data={
                'username': 'wronguser',
                'password': 'wronguserpasswd'
            }
        )
        self.assertNotEqual(302, response.status_code)


class TestLoginAuthenticationForm(TestCase):
    def setUp(self):
        self.user = CustomUser.objects._create_user(
            "testuser@codepoets.it",
            "testuserpasswd",
            False,
            False,
            CustomUser.UserType.EMPLOYEE.name,
        )

    def test_form_authentication_should_be_valid_with_existing_user_data(self):
        self.clean_data = {
            'username': 'testuser',
            'password': 'testuserpasswd'
        }
        form = LoginAuthentication(data=self.clean_data)
        self.assertTrue(form.is_valid())

    def test_form_authentication_should_be_not_valid_with_existing_user_data(self):
        self.clean_data = {
            'username': 'wrongtestuser',
            'password': 'wrongtestuserpasswd'
        }
        form = LoginAuthentication(data=self.clean_data)
        self.assertFalse(form.is_valid())
