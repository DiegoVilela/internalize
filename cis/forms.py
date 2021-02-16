from django import forms
from django_registration.forms import RegistrationForm

from .models import User


class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UploadCIsForm(forms.Form):
    file = forms.FileField()
