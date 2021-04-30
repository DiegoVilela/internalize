from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.utils.translation import ngettext
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.forms import inlineformset_factory
from django.core.exceptions import PermissionDenied

from .models import CI, Client, Place, Manufacturer, Appliance, CIPack
from .forms import UploadCIsForm, CIForm, ApplianceForm, PlaceForm
from .loader import CILoader
from .mixins import UserApprovedMixin, AddClientMixin


def homepage(request):
    user = request.user
    if not user.is_anonymous and not user.is_approved:
        messages.warning(request, 'Your account needs to be approved. '
                                  'Please contact you Account Manager.')
    return render(request, 'homepage.html')


class PlaceCreateView(UserApprovedMixin, SuccessMessageMixin, AddClientMixin, CreateView):
    model = Place
    fields = ('name', 'description')
    success_message = "The place %(name)s was created successfully."


class PlaceUpdateView(UserApprovedMixin, SuccessMessageMixin, UpdateView):
    model = Place
    fields = ('name', 'description')
    success_message = "The place %(name)s was updated successfully."

    def get_queryset(self):
        qs = Place.objects.select_related('client')
        if not self.request.user.is_superuser:
            qs.filter(client=self.request.user.client)
        return qs


@login_required
def manage_client_places(request):
    if not request.user.is_approved: raise PermissionDenied()

    client = request.user.client
    select_client_form = None
    if request.user.is_superuser:
        select_client_form = PlaceForm()

    if request.method == 'GET':
        if request.user.is_superuser:
            if (client_id_selected := request.GET.get('client')):
                # At this point, a client was selected by a superuser
                select_client_form = PlaceForm(request.GET)
                client = Client.objects.get(pk=client_id_selected)

    PlaceInlineFormSet = inlineformset_factory(
        Client, Place, fields=('name', 'description'), extra=0)
    formset = PlaceInlineFormSet(instance=client)

    if request.method == 'POST':
        formset = PlaceInlineFormSet(request.POST, instance=client)
        if formset.is_valid():
            formset.save()
            messages.success(request, "The places were updated successfully.")
            return redirect('cis:manage_client_places')

    return render(request, 'cis/manage_client_places.html', {
        'formset': formset,
        'select_client_form': select_client_form,
        'client': client,
    })


class CICreateView(UserApprovedMixin, SuccessMessageMixin, AddClientMixin, CreateView):
    model = CI
    form_class = CIForm
    success_message = "The CI was created successfully."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # only places of the user.client will be shown in the form
        kwargs.update({'client': self.request.user.client })
        return kwargs


class CIListView(UserApprovedMixin, ListView):
    model = CI
    paginate_by = 10

    def get_queryset(self):
        qs = CI.objects.filter(
            status=self.kwargs['status'],
            place__client=self.request.user.client
        )
        if self.request.user.is_superuser:
            qs = CI.objects.filter(status=self.kwargs['status'])

        return qs


class CIDetailView(UserApprovedMixin, DetailView):
    model = CI
    queryset = CI.objects.select_related('place', 'contract')

    def get_object(self, **kwargs):
        object = super().get_object(**kwargs)
        if not self.request.user.is_superuser:
            if object.place.client != self.request.user.client:
                # user authenticated but unauthorized
                raise Http404
        # user authenticated and authorized
        return object


class ManufacturerDetailView(UserApprovedMixin, DetailView):
    model = Manufacturer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Appliance.objects.filter(
            manufacturer=context['manufacturer'],
            client=self.request.user.client,
        )
        if self.request.user.is_superuser:
            qs = Appliance.objects.filter(manufacturer=context['manufacturer'])
        context['num_appliances'] = qs.count()

        return context


class ApplianceListView(UserApprovedMixin, ListView):
    model = Appliance
    paginate_by = 10

    def get_queryset(self):
        qs = Appliance.objects.filter(client=self.request.user.client)
        if self.request.user.is_superuser:
            qs = super().get_queryset()
        return qs


class ApplianceCreateView(UserApprovedMixin, SuccessMessageMixin, AddClientMixin, CreateView):
    model = Appliance
    form_class = ApplianceForm
    success_message = "The appliance %(serial_number)s was created successfully."


class ApplianceUpdateView(UserApprovedMixin, SuccessMessageMixin, UpdateView):
    model = Appliance
    form_class = ApplianceForm
    success_message = "The appliance was updated successfully."

    def get_queryset(self):
        qs = Appliance.objects.select_related('client', 'manufacturer')
        if not self.request.user.is_superuser:
            qs.filter(client=self.request.user.client)
        return qs

@login_required
def ci_upload(request):
    if not request.user.is_approved: raise PermissionDenied()

    result = None
    form = UploadCIsForm()

    if request.method == 'POST':
        form = UploadCIsForm(request.POST, request.FILES)
        if form.is_valid():
            client = request.user.client
            result = CILoader(request.FILES['file'], client).save()

    return render(request, 'cis/ci_upload.html', {
        'form': form,
        'result': result
    })


@login_required
def send_ci_pack(request):
    if not request.user.is_approved: raise PermissionDenied()

    if request.method == 'POST':
        try:
            pack = CIPack.objects.create(responsible=request.user)
            ci_pks = request.POST.getlist('cis_selected')
            if ci_pks:
                pack.send_to_production(ci_pks)
                messages.success(request, ngettext(
                    'The selected CI was sent to production successfully.',
                    'The selected CIs were sent to production successfully.',
                    len(ci_pks)
                ))
            else:
                messages.error(request, 'Please select at least one item to be sent to production.')
        except DatabaseError:
            raise DatabaseError('There was an error during the sending of the CIs to production.')

    return redirect('cis:ci_list', status=0)
