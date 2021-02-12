from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import CI, Client, Manufacturer, Appliance
from .forms import UploadCIsForm
from .loader import CILoader


class ClientListView(ListView):
    model = Client


class ClientDetailView(DetailView):
    model = Client


class CIListView(ListView):
    model = CI


class CIDetailView(DetailView):
    model = CI


class ManufacturerDetailView(DetailView):
    model = Manufacturer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_appliances'] = Appliance.objects.filter(
            manufacturer=context['manufacturer']
        ).count()
        return context


def ci_upload(request):
    result = None

    if request.method == 'POST':
        form = UploadCIsForm(request.POST, request.FILES)
        if form.is_valid():
            loader = CILoader(request.FILES['file'])
            result = loader.save()
    else:
        form = UploadCIsForm()

    return render(request, 'cis/ci_upload.html', {
        'form': form,
        'result': result
    })
