from django import forms
from django_registration.forms import RegistrationForm

from .models import User, CI, Site, Appliance


class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UploadCIsForm(forms.Form):
    file = forms.FileField()


class CIForm(forms.ModelForm):
    appliances = forms.ModelMultipleChoiceField(queryset=None)
    site = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client')
        super().__init__(*args, **kwargs)
        self.fields['appliances'] = forms.ModelMultipleChoiceField(
            queryset=Appliance.objects.filter(client=self.client)
        )
        self.fields['site'] = forms.ModelChoiceField(
            queryset=Site.objects.filter(client=self.client)
        )

    class Meta:
        model = CI
        exclude = ('client', 'status')


class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        exclude = ('client',)
