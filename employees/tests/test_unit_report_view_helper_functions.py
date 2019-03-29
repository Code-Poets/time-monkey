import datetime
from decimal import Decimal
from django.test import TestCase

from employees.models import Report
from employees.views import decimal_to_hours_string
from employees.views import hours_per_day_counter
from employees.views import hours_to_minutes
from employees.views import hours_per_month_counter
from employees.views import hours_string_to_decimal
from employees.views import minutes_to_hours
from employees.views import query_as_dict
from managers.models import Project
from users.models import CustomUser


class TestListHelpers(TestCase):
    def test_queryset_as_dict_should_return_dictionary_where_keys_are_dates_and_values_are_lists_of_reports_with_last_element_being_total_hours_value(self):
        user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            first_name='John',
            last_name='Doe',
            country='PL'
        )
        user.full_clean()
        user.save()

        project = Project(
            name="Test Project",
            start_date=datetime.datetime.now(),
        )
        project.full_clean()
        project.save()

        report_1 = Report(
            date=datetime.datetime.now().date(),
            description='Some description',
            author=user,
            project=project,
            work_hours=Decimal('8.00'),
        )
        report_1.full_clean()
        report_1.save()

        report_2 = Report(
            date=datetime.datetime.now().date(),
            description='Some description',
            author=user,
            project=project,
            work_hours=Decimal('8.00'),
        )
        report_2.full_clean()
        report_2.save()

        report_3 = Report(
            date=datetime.date(2001, 1, 1),
            description='Some description',
            author=user,
            project=project,
            work_hours=Decimal('8.00'),
        )
        report_3.full_clean()
        report_3.save()

        queryset = Report.objects.all()
        dictionary = query_as_dict(queryset)
        self.assertEqual(list(dictionary.keys())[0], datetime.datetime.now().date())
        self.assertEqual(list(dictionary.keys())[1], datetime.date(2001, 1, 1))
        self.assertEqual(dictionary[datetime.datetime.now().date()][0], report_1)
        self.assertEqual(dictionary[datetime.datetime.now().date()][1], report_2)
        self.assertEqual(dictionary[datetime.datetime.now().date()][2], '16:00')
        self.assertEqual(dictionary[datetime.date(2001, 1, 1)][0], report_3)
        self.assertEqual(dictionary[datetime.date(2001, 1, 1)][1], '8:00')

    def test_hours_to_minutes_should_return_amount_of_minutes_representing_amount_of_given_hours(self):
        self.assertEqual(hours_to_minutes(Decimal('2.30')), Decimal('150'))

    def test_minutes_to_hours_should_return_amount_of_hours_representing_amount_of_given_minutes(self):
        self.assertEqual(minutes_to_hours(Decimal('190')), Decimal('3.10'))

    def test_decimal_to_hours_string_should_return_string_with_accurate_hour_formatting_from_given_decimal(self):
        self.assertEqual(decimal_to_hours_string(Decimal('8.30')), '8:30')

    def test_hours_string_to_decimal_should_return_string_with_accurate_hour_formatting_from_given_decimal(self):
        self.assertEqual(hours_string_to_decimal('8:30'), Decimal('8.30'))

    def test_hours_per_day_counter_should_return_decimal_representing_total_work_hours_sum_from_given_list_of_reports(self):
        user = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            first_name='John',
            last_name='Doe',
            country='PL'
        )
        user.full_clean()
        user.save()

        project = Project(
            name="Test Project",
            start_date=datetime.datetime.now(),
        )
        project.full_clean()
        project.save()

        report_1 = Report(
            date=datetime.datetime.now().date(),
            description='Some description',
            author=user,
            project=project,
            work_hours=Decimal('8.00'),
        )
        report_1.full_clean()
        report_1.save()

        report_2 = Report(
            date=datetime.datetime.now().date(),
            description='Some description',
            author=user,
            project=project,
            work_hours=Decimal('8.00'),
        )
        report_2.full_clean()
        report_2.save()

        report_3 = Report(
            date=datetime.date(2001, 1, 1),
            description='Some description',
            author=user,
            project=project,
            work_hours=Decimal('8.00'),
        )
        report_3.full_clean()
        report_3.save()

        self.assertEqual(hours_per_day_counter([report_1, report_2, report_3]), Decimal('24.00'))

    def test_hours_per_month_counter_should_return_decimal_representing_total_work_hours_sum_from_given_dictionary_where_values_are_lists_containing_work_hours_string_at_the_end(self):
        dictionary = {
            0: ['reports', '8:00'],
            1: [5, None, '4:00'],
            2: ['6:00'],
        }
        self.assertEqual(hours_per_month_counter(dictionary), Decimal('18.00'))
