# Generated by Django 2.1.1 on 2018-11-13 12:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('start_date', models.DateField()),
                ('stop_date', models.DateField(blank=True, null=True)),
                ('terminated', models.BooleanField(default=False)),
                ('managers', models.ManyToManyField(related_name='managers', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
