from users.models import CustomUserPreferences


def user_preferences(request):
    if request.user.is_authenticated:
        preferences = CustomUserPreferences.objects.get(user=request.user)
        expanded_menu = preferences.expanded_menu
    else:
        expanded_menu = False
    return {"expanded_menu": expanded_menu}
