from typing import Any
from typing import Union

from django.db.models.base import ModelBase
from django.test.client import Client

from utils.e2e.base.base_components import AbstractClientHandler
from utils.e2e.base.base_components import AbstractDatabaseHandler


class DjangoClientHandler(AbstractClientHandler):
    _client = Client()

    def get(self, url: str) -> Any:
        return self._client.get(path=url)

    def post(self, url: str, data: dict) -> Any:
        return self._client.post(path=url, data=data)


class DjangoDatabaseHandler(AbstractDatabaseHandler):
    def does_object_exist(self, model_class: ModelBase, attributes: dict) -> bool:
        try:
            model_class.objects.get(*attributes.items())
            return True
        except model_class.DoesNotExist:
            return False

    def retrieve_object_id(self, model_class: ModelBase, attributes: dict) -> Union[int, None]:
        try:
            obj = model_class.objects.get(*attributes.items())
            return obj.id
        except model_class.DoesNotExist:
            return None

    def rollback(self):
        pass
