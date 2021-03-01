from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.forms import modelform_factory

from .models import CI, Client, Manufacturer, Appliance, CIPack, Setup, Credential
from .forms import UploadCIsForm
from .loader import CILoader
from .mixins import UserApprovedMixin


class HomePageView(TemplateView):
    template_name = 'cis/homepage.html'


class ClientListView(UserApprovedMixin, ListView):
    model = Client

    def get_queryset(self):
        pass


class ClientDetailView(UserApprovedMixin, DetailView):
    model = Client

    def get_context_data(self, **kwargs):
        print(self.request)
        return super().get_context_data(**kwargs)


def ci_create(request):
    CIForm = modelform_factory(CI, exclude=['setup', 'credential', 'status'])
    SetupForm = modelform_factory(Setup, fields='__all__')
    CredentialForm = modelform_factory(Credential, fields='__all__')

    if request.method == 'POST':
        form_ci = CIForm(request.POST)
        form_setup = SetupForm(request.POST)
        form_credential = CredentialForm(request.POST)

        if form_ci.is_valid() and form_setup.is_valid() and form_credential.is_valid():
            ci = form_ci.save(commit=False)
            ci.setup = form_setup.save()
            ci.credential = form_credential.save()
            ci.save()
            # save appliances as it is a many-to-many relationship
            # https://docs.djangoproject.com/en/3.1/topics/forms/modelforms/#the-save-method
            form_ci.save_m2m()
            return redirect(reverse('cis:ci_detail', args=[ci.pk]))
        else:
            return render(request, 'cis/ci_form.html', {
                'form_ci': form_ci,
                'form_setup': form_setup,
                'form_credential': form_credential,
            })
    else:
        form_ci = CIForm()
        form_setup = SetupForm()
        form_credential = CredentialForm()

    return render(request, 'cis/ci_form.html', {
        'form_ci': form_ci,
        'form_setup': form_setup,
        'form_credential': form_credential,
    })


class CIListView(LoginRequiredMixin, ListView):
    model = CI

    def get_queryset(self):
        return CI.objects.filter(status=self.kwargs['status'])


class CIDetailView(UserApprovedMixin, DetailView):
    model = CI


class ManufacturerDetailView(UserApprovedMixin, DetailView):
    model = Manufacturer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_appliances'] = Appliance.objects.filter(
            manufacturer=context['manufacturer']
        ).count()
        return context


class ApplianceCreateView(UserApprovedMixin, CreateView):
    model = Appliance
    fields = '__all__'


class ApplianceUpdateView(UserApprovedMixin, UpdateView):
    model = Appliance
    fields = '__all__'


class SetupCreateView(UserApprovedMixin, CreateView):
    model = Setup
    fields = '__all__'


class SetupUpdateView(UserApprovedMixin, UpdateView):
    model = Setup
    fields = '__all__'


class CredentialCreateView(UserApprovedMixin, CreateView):
    model = Credential
    fields = '__all__'


class CredentialUpdateView(UserApprovedMixin, UpdateView):
    model = Credential
    fields = '__all__'


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
