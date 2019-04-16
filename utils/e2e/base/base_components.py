from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import Union


class AbstractClientHandler(ABC):
    @property
    @abstractmethod
    def _client(self) -> object:
        return NotImplemented

    @abstractmethod
    def get(self, url: str) -> Any:
        return NotImplemented

    @abstractmethod
    def post(self, url: str, data: dict) -> Any:
        return NotImplemented


class AbstractDatabaseHandler(ABC):
    @abstractmethod
    def does_object_exist(self, model_class: type, attributes: dict) -> bool:
        return NotImplemented

    @abstractmethod
    def retrieve_object_id(self, model_class: type, attributes: dict) -> Union[int, None]:
        return NotImplemented

    @abstractmethod
    def rollback(self):
        pass


class BaseStep:
    _test_case: "BaseE2ETest"
    _client: AbstractClientHandler
    _database_handler: AbstractDatabaseHandler
    attributes = {}  # type: Dict[Any, Any]
    required_attributes: List[str]

    def __init__(self, test_case: "BaseE2ETest", attributes: Dict[Any, Any]):
        self._test_case = test_case
        self._client = test_case.client_handler
        self.attributes.update(**attributes)
        self._database_handler = test_case.database_handler

    @abstractmethod
    def run_tests(self):
        return NotImplemented

    def run(self):
        self.attributes = self.get_attributes()
        self.run_tests()

    def get_attributes(self):
        return self.attributes

    def _create_object(self, model_class: type, attributes: dict, url: str, non_model_fields: dict = None):
        signup_attributes = {**attributes.copy(), **non_model_fields}
        self._client.get(url=url)
        self._client.post(url=url, data=signup_attributes)
        self._test_object_exists_in_database(model_class, attributes)

    def _edit_object(self, object_edit_url: str, target_object_data: dict, target_field: str, target_value: Any):
        modified_target_object_data = target_object_data.copy()
        modified_target_object_data[target_field] = target_value
        self._client.get(url=object_edit_url)
        response = self._client.post(url=object_edit_url, data=modified_target_object_data)

        if response.status_code == 302:
            print("User data successfully modified!")
            print("Searching for updated user...")
            from users.models import CustomUser

            self._test_object_exists_in_database(CustomUser, modified_target_object_data)
        else:
            print("User data was not modified due to an error!")

    def _delete_object(self):
        pass

    def _sign_in_user(self, username: str, password: str, url: str):
        self._client.get(url=url)
        response = self._client.post(url=url, data={"username": username, "password": password})
        logged_user = response.wsgi_request.user
        if username in logged_user.__dict__.values():
            print(f"- User logged in! -")
        else:
            print(f"- User was not logged in! -")

    def _get_field_from_model_attributes(self, attributes_key: str, field_key: str):
        return self.attributes[attributes_key][self.attributes[field_key]]

    def _test_object_exists_in_database(self, model_class: type, attributes: dict):
        if self._database_handler.does_object_exist(model_class=model_class, attributes=attributes):
            print(f"{model_class.__name__} object exists in database")
        else:
            print(f"{model_class.__name__} does not exist in database!")


class BaseE2ETest:
    steps: List[Type[BaseStep]]
    attributes: Dict[Any, Any]
    client_handler: AbstractClientHandler
    database_handler: AbstractDatabaseHandler
    _attr_list: List[Dict[Any, Any]]

    def test(self):
        self.set_up()
        self._attr_list = self.list_attributes()
        self.run_steps()
        self.rollback()

    def set_up(self):
        pass

    def list_attributes(self) -> List[Dict[Any, Any]]:
        attr_list = []
        for step in self.steps:
            step_attributes = {}
            for attribute in step.required_attributes:
                step_attributes[attribute] = self.attributes.get(attribute, None)
            attr_list.append(step_attributes)
        return attr_list

    def run_steps(self):
        for i in range(len(self.steps)):
            s = self.steps[i](test_case=self, attributes=self._attr_list[i])
            s.run()

    def rollback(self):
        self.database_handler.rollback()


class InitUser(BaseStep):
    required_attributes = [
        "user_class",
        "user_attributes",
        "username_field",
        "password_field",
        "signup_url",
        "login_url",
        "extra_signup_attributes",
    ]

    def run_tests(self):
        print("### Initializing user ###")
        print("1. Registering new user:")
        self._create_object(
            model_class=self.attributes["user_class"],
            attributes=self.attributes["user_attributes"],
            url=self.attributes["signup_url"],
            non_model_fields=self.attributes.get("extra_signup_attributes", None),
        )
        print("2. Logging in as newly created user:")
        self._sign_in_user(
            username=self._get_field_from_model_attributes("user_attributes", "username_field"),
            password=self._get_field_from_model_attributes("extra_signup_attributes", "password_field"),
            url=self.attributes["login_url"],
        )
        print("### User successfully initialized ###")
