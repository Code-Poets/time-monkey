import datetime

import factory
import factory.fuzzy

from employees.models import ActivityType
from employees.models import Report


class ReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Report

    date = factory.Faker("date")
    author = factory.SubFactory("users.factories.UserFactory")
    project = factory.SubFactory("managers.factories.ProjectFactory")
    work_hours = factory.LazyFunction(lambda: datetime.timedelta(hours=8))
    description = factory.fuzzy.FuzzyText()
    activities = factory.SubFactory("employees.factories.ActivityTypeFactory")


class ActivityTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ActivityType

    name = factory.fuzzy.FuzzyChoice(["Review", "Backend Development", "Frontend Development", "Meeting"])
