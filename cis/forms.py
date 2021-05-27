from django import forms

from .models import CI, Place, Appliance


class UploadCIsForm(forms.Form):
    file = forms.FileField()


class CIForm(forms.ModelForm):
    appliances = forms.ModelMultipleChoiceField(queryset=None)
    place = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client')
        super().__init__(*args, **kwargs)
        self.fields['appliances'] = forms.ModelMultipleChoiceField(
            queryset=Appliance.objects.filter(client=self.client)
        )
        self.fields['place'] = forms.ModelChoiceField(
            queryset=Place.objects.filter(client=self.client)
        )

    class Meta:
        model = CI
        exclude = ('client', 'status', 'pack')


class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        exclude = ('client',)


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('client',)
