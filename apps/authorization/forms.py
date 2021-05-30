from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from random import random
import hashlib
from .models import HabrUser


class HabrUserLoginForm(AuthenticationForm):
    """
    форма отвечающая за авторизацию
    """

    def __init__(self, *args, **kwargs):
        super(HabrUserLoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = HabrUser
        fields = ("username", "password")


class HabrUserRegisterForm(UserCreationForm):
    """
    форма отвечающая за регистрацию
    """

    def __init__(self, *args, **kwargs) -> None:
        super(HabrUserRegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.help_text = ""

    class Meta:
        model = HabrUser
        fields = ("email", "username", "password1", "password2")

    def save(self, **kwargs):
        user = super().save()
        user.is_active = False
        salt = hashlib.sha256(str(random()).encode('utf-8')).hexdigest()[:6]
        user.activation_key = hashlib.sha256((user.email + salt).encode('utf-8')).hexdigest()
        user.save()
        return user
