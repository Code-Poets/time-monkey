from django.test import TestCase

from users.models import CustomUser
from utils.e2e.base.base_components import InitUser

from .steps import E2ETest
from .steps import InitManager


class TestUserCreation(TestCase, E2ETest):
    steps = [InitUser]

    def list_attributes(self):
        self.attributes["user_attributes"] = {"email": "example@codepoets.it"}
        self.attributes["extra_signup_attributes"] = {"password1": "passwduser", "password2": "passwduser"}
        return super().list_attributes()


class TestManagerCreation(TestCase, E2ETest):
    steps = [InitManager]

    def set_up(self):
        print("* Creating admin user *")
        CustomUser.objects.create_superuser(email="admin@codepoets.it", password="superuser")
        print("* Admin saved *")

    def list_attributes(self):
        self.attributes["user_attributes"] = {"email": "example@codepoets.it"}
        self.attributes["extra_signup_attributes"] = {"password1": "passwduser", "password2": "passwduser"}
        self.attributes["admin_username"] = "admin@codepoets.it"
        self.attributes["admin_password"] = "superuser"
        return super().list_attributes()
