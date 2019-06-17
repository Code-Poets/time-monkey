from django.urls import reverse

from users.models import CustomUser
from utils.e2e.base.base_components import BaseE2ETest
from utils.e2e.base.base_components import BaseStep
from utils.e2e.django_components import DjangoClientHandler
from utils.e2e.django_components import DjangoDatabaseHandler


class E2ETest(BaseE2ETest):
    client_handler = DjangoClientHandler()
    database_handler = DjangoDatabaseHandler()
    attributes = {
        "user_class": CustomUser,
        "username_field": "email",
        "password_field": "password1",
        "signup_url": "/signup/",
        "login_url": "/accounts/login/",
    }


class InitManager(BaseStep):
    required_attributes = [
        "user_class",
        "user_attributes",
        "username_field",
        "password_field",
        "signup_url",
        "login_url",
        "extra_signup_attributes",
        "admin_username",
        "admin_password",
        "target_field",
        "target_value",
    ]

    def get_attributes(self):
        attributes = super().get_attributes()
        attributes["target_field"] = "user_type"
        attributes["target_value"] = "MANAGER"
        return attributes

    def run_tests(self):
        print("### Initializing manager ###")
        print("1. Registering new user:")
        self._create_object(
            model_class=self.attributes["user_class"],
            attributes=self.attributes["user_attributes"],
            url=self.attributes["signup_url"],
            non_model_fields=self.attributes["extra_signup_attributes"],
        )
        print("2. Logging in as newly created user:")
        self._sign_in_user(
            username=self._get_field_from_model_attributes("user_attributes", "username_field"),
            password=self._get_field_from_model_attributes("extra_signup_attributes", "password_field"),
            url=self.attributes["login_url"],
        )
        print("3. Logging in as an administrator:")
        self._client = self._client.__class__()
        self._sign_in_user(
            username=self.attributes["admin_username"],
            password=self.attributes["admin_password"],
            url=self.attributes["login_url"],
        )
        user_edit_url = reverse(
            "custom-user-update-by-admin",
            kwargs={
                "pk": self._database_handler.retrieve_object_id(
                    self.attributes["user_class"], self.attributes["user_attributes"]
                )
            },
        )
        print("4. Changing user type:")
        self._edit_object(
            object_edit_url=user_edit_url,
            target_object_data=self.attributes["user_attributes"],
            target_field=self.attributes["target_field"],
            target_value=self.attributes["target_value"],
        )
        print("### Manager successfully initialized ###")
