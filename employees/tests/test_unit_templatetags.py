from datetime import timedelta

import pytest
from assertpy import assert_that
from django.db.models.functions import datetime
from django.test import TestCase

from employees.templatetags.data_display_filters import convert_to_month_name
from employees.templatetags.data_display_filters import duration_field_to_string
from employees.templatetags.data_display_filters import extract_year_and_month_from_url
from employees.templatetags.data_structure_element_selectors import get_key_value


class GetKeyValueTests(TestCase):
    def setUp(self):
        self.dictionary = {"one": 1, "two": 2, "three": 3}

    def test_get_key_value_function_should_return_an_element_of_given_dict_at_given_key(self):
        result = get_key_value(self.dictionary, "two")
        self.assertEqual(result, 2)

    def test_get_key_value_function_should_return_empty_string_on_incorrect_key(self):
        result = get_key_value(self.dictionary, 2)
        self.assertEqual(result, "")


class DurationHoursTests(TestCase):
    def test_duration_field_to_string_should_parse_duration_to_string(self):
        self.assertEqual(duration_field_to_string(timedelta(hours=8)), "08:00")


class TestExtractionTag:
    @pytest.mark.parametrize(
        ("url", "date"),
        [
            ("/felicita/felicita/felicita/felicita/2019/4", ["2019", "4"]),
            ("/mamma/mia/mamma/mia/2018/9", ["2018", "9"]),
            ("/kazde/pokolenie/ma/wlasny/2100/1", ["2100", "1"]),
        ],
    )  # pylint: disable=no-self-use
    def test_extract_year_and_month_from_url_function_should_correct_extract_year_and_month(self, url, date):
        assert_that(extract_year_and_month_from_url(url)).is_equal_to(date)

    @pytest.mark.parametrize(
        "url",
        [
            "/felicita/felicita/felicita/2019/4/felicita",
            "/mamma/mia/mamma/2018/9/mia",
            "/kazde/pokolenie/ma/2100/1/wlasny",
        ],
    )  # pylint: disable=no-self-use
    def test_if_function_get_incorrect_url_should_return_current_year_and_month(self, url):
        assert_that(extract_year_and_month_from_url(url)).is_equal_to(
            [datetime.datetime.now().year, datetime.datetime.now().month]
        )


class TestConvertToMonthName:
    @pytest.mark.parametrize(
        ("month_number", "month"), [(1, "January"), ("4", "April"), (6, "June"), ("12", "December")]
    )  # pylint: disable=no-self-use
    def test_function_convert_correctly_numbers_to_months_names(self, month_number, month):
        assert_that(convert_to_month_name(month_number)).is_equal_to(month)

    def test_function_raise_value_error_if_value_is_not_a_string_number(self):  # pylint: disable=no-self-use
        with pytest.raises(ValueError):
            convert_to_month_name("June")

    def test_function_raise_index_error_if_value_is_out_of_range(self):  # pylint: disable=no-self-use
        with pytest.raises(IndexError):
            convert_to_month_name("13")
