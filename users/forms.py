from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django_countries.widgets import CountrySelectWidget
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
        if "@" not in username:
            username = username + "@codepoets.it"
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
