# Generated by Django 2.2.2 on 2019-07-09 09:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20190703_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='expected_weekly_hours',
            field=models.DurationField(default='00:00:00'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_enabled_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='reporting_managers',
            field=models.ManyToManyField(default=None, related_name='_customuser_reporting_managers_+', to=settings.AUTH_USER_MODEL),
        ),
    ]
