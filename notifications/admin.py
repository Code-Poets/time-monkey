from django.contrib import admin

from notifications.models import Notification
from notifications.models import NotificationEnabledForUser


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "receiver", "project", "type", "created_at", "is_read_at")
    list_filter = ("type",)
    search_fields = ("user__email", "receiver__email", "project__name")


@admin.register(NotificationEnabledForUser)
class NotificationEnabledForUserAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "is_enabled", "modified_at", "modified_by", "values")
    list_filter = ("type",)
    search_fields = ("user__email", "values")
