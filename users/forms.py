from typing import Any
from typing import Dict

from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.mixins import CreateUpdateAjaxMixin
from captcha.fields import CaptchaField
from captcha.fields import CaptchaTextInput
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from users.common.constants import CaptchaConstants
from users.common.constants import UserConstants
from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm, BSModalModelForm, CreateUpdateAjaxMixin):
    password1 = forms.CharField(label="", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="", widget=forms.PasswordInput, help_text="Enter the same password as above, for verification."
    )

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "user_type")
        labels = {"email": "", "first_name": "", "last_name": "", "user_type": ""}

    def save(self, commit: bool = False) -> object:
        # pylint: disable=E1003
        if not self.request.is_ajax():
            instance = super(CreateUpdateAjaxMixin, self).save(commit=commit)
            instance.save()
        else:
            instance = super(CreateUpdateAjaxMixin, self).save(commit=False)

        return instance


class SimpleUserChangeForm(ModelForm):
    """
    A form for updating users by EMPLOYEE users.
    """

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name")


class AdminUserChangeForm(BSModalModelForm):
    """
    A form for updating users by ADMIN users. Includes more fields than `SimpleUserChangeForm`.
    """

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "user_type")
        labels = {"email": "", "first_name": "", "last_name": "", "user_type": ""}


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all fields from user model,
    but replaces the password field with admin's
    password hash display field.
    """

    class Meta:
        model = CustomUser
        fields = "__all__"

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_is_active = cleaned_data.get("is_active")
        if self.instance.is_active and not cleaned_is_active:
            cleaned_data["user_type"] = CustomUser.UserType.EMPLOYEE.name
            cleaned_data["is_staff"] = False
            cleaned_data["is_superuser"] = False

        return cleaned_data


class CustomUserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=UserConstants.EMAIL_MAX_LENGTH.value, required=True, label="id_email")
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={"placeholder": CaptchaConstants.PLACE_HOLDER_CAPTCHA.value}))

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2", "captcha")
