from django import template
from django.db.models import Q
register = template.Library()


@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)


@register.filter
def filter_id(queryset, value):
    return queryset.filter(id=value)


@register.filter
def filter_start_date(queryset, value):
    return queryset.filter(start_date=value)


@register.filter
def filter_stop_date(queryset, value):
    return queryset.filter(stop_date=value)


@register.filter
def filter_terminated(queryset):
    return queryset.filter(terminated=True, stop_date=None)


@register.filter
def filter_active(queryset):
    return queryset.filter(terminated=False, stop_date=None)


@register.filter
def filter_completed(queryset):
    return queryset.filter(~Q(stop_date=None))
