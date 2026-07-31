from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from .models import username_validator


class RegistrationForm(forms.Form):
    email = forms.EmailField(max_length=254)
    password = forms.CharField(strip=False)
    username = forms.CharField(min_length=3, max_length=30)
    display_name = forms.CharField(min_length=1, max_length=50, strip=True)
    is_private = forms.NullBooleanField(required=True)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"].lower()
        username_validator(username)
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        password_validation.validate_password(password)
        return password

    def save(self):
        return get_user_model().objects.create_user(**self.cleaned_data)


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254)
    password = forms.CharField(strip=False)

    def clean_email(self):
        return self.cleaned_data["email"].lower()
