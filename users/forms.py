from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django_countries.widgets import CountrySelectWidget

from users.common.constants import VALID_EMAIL_DOMAIN_LIST
from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, without privileges,
    from given email and password.
    """
    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all fields from user model,
    but replaces the password field with admin's
    password hash display field.
    """
    class Meta:
        model = CustomUser
        fields = '__all__'
        widgets = {'country': CountrySelectWidget()}


class LoginAuthentication(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        domain_list_size = len(VALID_EMAIL_DOMAIN_LIST) - 1

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)

            while self.user_cache is None and domain_list_size >= 0:
                username_temp = username + VALID_EMAIL_DOMAIN_LIST[domain_list_size]
                self.user_cache = authenticate(self.request, username=username_temp, password=password)
                domain_list_size -= 1

            if self.user_cache is None:
                raise self.get_invalid_login_error()

        return self.cleaned_data
