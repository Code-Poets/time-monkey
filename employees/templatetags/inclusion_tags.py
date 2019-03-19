from django import template
from django.urls import reverse
from django.utils import timezone
from employees.common.strings import MonthNavigationText
from employees.forms import MonthSwitchForm

from employees.common.constants import MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE

register = template.Library()


def get_previous_month_url(url_name, year, month, pk=None):
    if month is 1:
        year = year - 1
        month = 12
    else:
        month = month - 1
    if pk is None:
        return reverse(url_name, kwargs={'year': year, 'month': month})
    return reverse(url_name, kwargs={'pk': pk, 'year': year, 'month': month})


def get_next_month_url(url_name, year, month, pk=None):
    if month is 12:
        year = year + 1
        month = 1
    else:
        month = month + 1
    if pk is None:
        return reverse(url_name, kwargs={'year': year, 'month': month})
    return reverse(url_name, kwargs={'pk': pk, 'year': year, 'month': month})


def get_recent_month_url(url_name, pk=None):
    month = timezone.now().date().month
    year = timezone.now().date().year
    if pk is None:
        return reverse(url_name, kwargs={'year': year, 'month': month})
    return reverse(url_name, kwargs={'pk': pk, 'year': year, 'month': month})


@register.inclusion_tag('employees/month_navigation_bar.html', takes_context=True)
def month_navigator(context, url_name, year, month, pk=None):
    disable_next_button = False
    disable_previous_button = False

    if month == MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE and year == MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE:
        disable_next_button = True
    elif month == MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE and year == MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE:
        disable_previous_button = True

    return {
        'path': context.request.path,
        'UI_text': MonthNavigationText,
        'month_form': MonthSwitchForm(year, month),
        'next_month_url': get_next_month_url(url_name, year, month, pk),
        'recent_month_url': get_recent_month_url(url_name, pk),
        'previous_month_url': get_previous_month_url(url_name, year, month, pk),
        'disable_next_button': disable_next_button,
        'disable_previous_button': disable_previous_button,
    }