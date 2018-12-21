from django import forms
from django.db.models import QuerySet

from managers.models import Project
from users.models import CustomUser


class ProjectJoinForm(forms.Form):

    projects = forms.ChoiceField(choices=[])

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert isinstance(queryset, QuerySet)
        # assert isinstance(queryset.model, Project)      No exception message supplied
        self.fields['projects'].choices = [(project.id, project.name) for project in queryset]
