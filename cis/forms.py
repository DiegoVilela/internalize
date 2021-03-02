from django import forms
from django_registration.forms import RegistrationForm

from .models import User, CI, Site, Appliance


class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UploadCIsForm(forms.Form):
    file = forms.FileField()


class CIForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client')
        self.base_fields['appliances'] = forms.ModelMultipleChoiceField(
            queryset=Appliance.objects.filter(ci__site__client=self.client)
        )
        self.base_fields['site'] = forms.ModelChoiceField(
            queryset=Site.objects.filter(client=self.client)
        )
        super().__init__(*args, **kwargs)

    class Meta:
        model = CI
        exclude = ('status',)
