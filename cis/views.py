from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404

from .models import CI, Client, Manufacturer, Appliance, CIPack
from .forms import UploadCIsForm, CIForm, ApplianceForm
from .loader import CILoader
from .mixins import UserApprovedMixin


class HomePageView(TemplateView):
    template_name = 'cis/homepage.html'


class ClientListView(UserApprovedMixin, ListView):
    model = Client


class ClientDetailView(UserApprovedMixin, DetailView):
    model = Client

    def get_context_data(self, **kwargs):
        print(self.request)
        return super().get_context_data(**kwargs)


class CICreateView(UserApprovedMixin, CreateView):
    model = CI
    form_class = CIForm

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # only sites of the user.client will be shown
        kwargs.update({'client': self.request.user.client })
        return kwargs


class CIListView(UserApprovedMixin, ListView):
    model = CI

    def get_queryset(self):
        return CI.objects.filter(
            status=self.kwargs['status'],
            site__client=self.request.user.client
        )


class CIDetailView(UserApprovedMixin, DetailView):
    model = CI

    def get_object(self, **kwargs):
        object = super().get_object(**kwargs)
        if object.site.client != self.request.user.client:
            raise Http404
        return object


class ManufacturerDetailView(UserApprovedMixin, DetailView):
    model = Manufacturer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_appliances'] = Appliance.objects.filter(
            manufacturer=context['manufacturer']
        ).count()
        return context


class ApplianceListView(UserApprovedMixin, ListView):
    model = Appliance

    def get_queryset(self):
        return Appliance.objects.filter(client=self.request.user.client)


class ApplianceCreateView(UserApprovedMixin, CreateView):
    model = Appliance
    form_class = ApplianceForm

    def form_valid(self, form):
        form.instance.client = self.request.user.client
        return super().form_valid(form)


class ApplianceUpdateView(UserApprovedMixin, UpdateView):
    model = Appliance
    form_class = ApplianceForm


@login_required
def ci_upload(request):
    if not request.user.is_approved:
        messages.warning(request, 'Your account needs to be approved. Please contact you Account Manager.')
        return redirect('cis:homepage')

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


@login_required
def send_ci_pack(request):
    if not request.user.is_approved:
        messages.warning(request, 'Your account needs to be approved. Please contact you Account Manager.')
        return redirect('cis:homepage')

    if request.method == 'POST':
        pack = CIPack(responsible=request.user)
        pack.save()
        pack.items.set(request.POST.getlist('cis'))

        if pack.id:
            pack.send()
            messages.success(request, 'Pack created.')

    return render(request, 'cis/homepage.html')
