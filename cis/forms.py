from django import forms


class UploadCIsForm(forms.Form):
    file = forms.FileField()
