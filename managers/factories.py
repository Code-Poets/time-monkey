import factory
import factory.fuzzy
from factory.django import DjangoModelFactory

from managers.models import Project


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Faker("sentence", nb_words=3)
    start_date = factory.Faker("date")
