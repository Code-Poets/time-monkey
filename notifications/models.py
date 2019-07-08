from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import ForeignKey

from managers.models import Project
from notifications.constants import NotificationTypeConstants
from users.common.fields import ChoiceEnum
from users.models import CustomUser


class NotificationType(ChoiceEnum):
    DID_NOT_REPORT_FOR_DAYS = "DID_NOT_REPORT_FOR_DAYS"
    HAS_LESS_HOURS_IN_WEEK = "HAS_LESS_HOURS_IN_WEEK"
    HAS_MORE_HOURS_IN_WEEK = "HAS_MORE_HOURS_IN_WEEK"
    HAS_LESS_PERCENTAGE_OF_HOURS_IN_WEEK = "HAS_LESS_PERCENTAGE_OF_HOURS_IN_WEEK"
    HAS_MORE_PERCENTAGE_OF_HOURS_IN_WEEK = "HAS_MORE_PERCENTAGE_OF_HOURS_IN_WEEK"
    USER_WEEKLY_HOURS = "USER_WEEKLY_HOURS"
    HAS_LESS_HOURS_IN_DAY = "HAS_LESS_HOURS_IN_DAY"
    HAS_MORE_HOURS_IN_DAY = "HAS_MORE_HOURS_IN_DAY"


class Notification(models.Model):
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notification_user")
    receiver = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notification_receiver")
    project = ForeignKey(Project, on_delete=models.CASCADE, related_name="notification_project")
    type = CharField(choices=NotificationType.choices(), max_length=NotificationTypeConstants.length.value)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read_at = models.DateTimeField(null=True)


class NotificationEnabledForUser(models.Model):
    user = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notification_user_enabled")
    type = CharField(choices=NotificationType.choices(), max_length=NotificationTypeConstants.length.value)
    is_enabled = BooleanField(default=False)
    values = JSONField()
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notification_modified_by_user")
