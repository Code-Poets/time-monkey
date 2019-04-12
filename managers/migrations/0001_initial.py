# Generated by Django 2.1.1 on 2019-04-12 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
            ],
        ),
    ]
