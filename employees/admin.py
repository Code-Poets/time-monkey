from django.contrib import admin

from employees.models import ActivityType
from employees.models import Report

admin.site.register(Report)


class Activities(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(ActivityType, Activities)
