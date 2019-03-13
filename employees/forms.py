from django import forms
from django.db.models import QuerySet

from employees.common.constants import MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE


class ProjectJoinForm(forms.Form):

    projects = forms.ChoiceField(choices=[])

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert isinstance(queryset, QuerySet)
        self.fields['projects'].choices = [(project.id, project.name) for project in queryset]


class MonthSwitchForm(forms.Form):

    month = forms.IntegerField(
        min_value=MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE,
        max_value=MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE,
    )
    year = forms.IntegerField(
        min_value=MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE,
        max_value=MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE,
    )

    def __init__(self, year, month, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].initial = month
        self.fields['year'].initial = year
