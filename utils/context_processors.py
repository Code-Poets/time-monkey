from typing import Dict

from django.http import HttpRequest

from users.models import CustomUserPreferences


def user_preferences(request: HttpRequest) -> Dict[str, bool]:
    if request.user.is_authenticated:
        preferences = CustomUserPreferences.objects.get(user=request.user)
        expanded_menu = preferences.expanded_menu
    else:
        expanded_menu = False
    return {"expanded_menu": expanded_menu}
