from django.db import migrations


def add_preferences_for_users(apps, _schema_editor):
    CustomUser = apps.get_model("users", "CustomUser")
    CustomUserPreferences = apps.get_model("users", "CustomUserPreferences")
    preferences = [CustomUserPreferences(user=user) for user in CustomUser.objects.all()]
    CustomUserPreferences.objects.bulk_create(preferences)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_customuserpreferences"),
    ]

    operations = [
        migrations.RunPython(add_preferences_for_users),
    ]
