# Generated by Django 2.2.2 on 2019-07-09 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managers', '0003_auto_20190506_0733'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_enabled_notifications',
            field=models.BooleanField(default=True),
        ),
    ]
