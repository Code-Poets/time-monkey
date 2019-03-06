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

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            for domain in VALID_EMAIL_DOMAIN_LIST:
                if self.user_cache is not None:
                    break
                self.user_cache = authenticate(
                    self.request,
                    username=username + '@' + domain,
                    password=password,
                )

            if self.user_cache is None:
                raise self.get_invalid_login_error()

        return self.cleaned_data
