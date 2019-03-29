import datetime

from django.http import HttpRequest
from django.template import RequestContext
from django.template import Template
from django.test import TestCase

from employees.templatetags.inclusion_tags import get_next_month_url
from employees.templatetags.inclusion_tags import get_previous_month_url
from employees.templatetags.inclusion_tags import get_recent_month_url


class TestMonthNavigationHelpers(TestCase):
    def test_get_next_month_url_should_generate_url_for_next_month_for_given_path(self):
        self.assertEqual(get_next_month_url('project-report-list', 2018, 12, 1), '/reports/project/1/2019/1/')

    def test_get_previous_month_url_should_generate_url_for_previous_month_for_given_path(self):
        self.assertEqual(get_previous_month_url('project-report-list', 2019, 1, 1), '/reports/project/1/2018/12/')

    def test_get_recent_month_url_should_generate_url_for_current_month_for_given_path(self):
        current_date = datetime.datetime.now()
        self.assertEqual(get_recent_month_url('project-report-list', 1), f'/reports/project/1/{current_date.year}/{current_date.month}/')


class TestMonthNavigator(TestCase):
    def test_month_navigator_should_render_html_with_links_to_other_months_for_given_url(self):
        request = HttpRequest()
        request.path = '/reports/project/1/2019/3/'
        context = RequestContext(request=request)
        template_to_render = Template(
            "{% load inclusion_tags %}"
            "{% month_navigator 'project-report-list' 2019 1 1 %}"
        )
        rendered_template = template_to_render.render(context)
        current_date = datetime.datetime.now()
        self.assertTrue('<a href="/reports/project/1/2018/12/" class="btn btn-info">' in rendered_template)
        self.assertTrue(f'<a href="/reports/project/1/{current_date.year}/{current_date.month}/" class="btn btn-info">' in rendered_template)
        self.assertTrue('<a href="/reports/project/1/2019/2/" class="btn btn-info">' in rendered_template)

    def test_month_navigator_should_render_html_with_month_navigation_form_related_to_post_method_under_request_path(self):
        request = HttpRequest()
        request.path = '/reports/project/1/2019/3/'
        context = RequestContext(request=request)
        template_to_render = Template(
            "{% load inclusion_tags %}"
            "{% month_navigator 'project-report-list' 2018 10 2 %}"
        )
        rendered_template = template_to_render.render(context)
        self.assertTrue('<form action="/reports/project/1/2019/3/" method="POST">' in rendered_template)
