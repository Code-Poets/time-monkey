from decimal import Decimal

from django.utils.translation import ugettext_lazy


class ReportModelConstants:
    MAX_DESCRIPTION_LENGTH = 256
    MAX_DIGITS = 4
    DECIMAL_PLACES = 2
    MAX_WORK_HOURS = Decimal('24.00')
    MIN_WORK_HOURS = Decimal('0.01')
    MAX_WORK_HOURS_DECIMAL_VALUE = Decimal('0.59')
    MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE = ugettext_lazy('Ensure this value is less than or equal to ')
