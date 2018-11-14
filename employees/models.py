from django.db import models
from django.core.validators import BaseValidator
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator

from employees.common.constants import ReportModelConstants
from managers.models import Project
from users.models import CustomUser


class MaxDecimalValueValidator(BaseValidator):
    message = ReportModelConstants.MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE + '%(limit_value)s.'
    code = 'max_decimal_value'

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return x % 1


class Report(models.Model):
    date = models.DateField()
    description = models.CharField(
        max_length=ReportModelConstants.MAX_DESCRIPTION_LENGTH,
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
    )
    last_update = models.DateTimeField(
        auto_now=True,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    work_hours = models.DecimalField(
        max_digits=ReportModelConstants.MAX_DIGITS,
        decimal_places=ReportModelConstants.DECIMAL_PLACES,
        validators=
        [
            MinValueValidator(ReportModelConstants.MIN_WORK_HOURS),
            MaxValueValidator(ReportModelConstants.MAX_WORK_HOURS),
            MaxDecimalValueValidator(ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE),
        ]
    )
    editable = models.BooleanField(
        default=True,
    )
