import assertpy
import pytest
from django.utils import timezone

from utils.helpers import format_timedelta_to_hours_and_minutes_only


class TestTimeDeltaFormatting:
    @pytest.mark.parametrize(
        "timedelta,expected_output",
        [
            (timezone.timedelta(days=2, hours=5, minutes=30, seconds=15), "53:30"),
            (timezone.timedelta(minutes=72), "1:12"),
            (timezone.timedelta(seconds=1958), "0:32"),
        ],
    )
    def test_format_timedelta_to_hours_and_minutes_only_should_correctly_output_a_timedelta_value(
        self, timedelta, expected_output
    ):  # pylint: disable=no-self-use
        output = format_timedelta_to_hours_and_minutes_only(timedelta)
        assertpy.assert_that(output).is_equal_to(expected_output)
