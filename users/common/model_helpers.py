from users import models


def create_user_using_full_clean_and_save(email, first_name, last_name, password):
    user = models.CustomUser(email=email, first_name=first_name, last_name=last_name)
    user.set_password(password)
    user.full_clean()
    user.save()
    return user


def activate_user(user):
    user.is_active = True
    user.full_clean()
    user.save()
    user_preferences = models.CustomUserPreferences(user=user)
    user_preferences.full_clean()
    user_preferences.save()
