from django.db import DatabaseError
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.forms import inlineformset_factory
from django.core.exceptions import PermissionDenied

from .models import CI, Client, Place, Manufacturer, Appliance, CIPack
from .forms import UploadCIsForm, CIForm, ApplianceForm
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
    queryset = Place.objects.select_related('client')
    success_message = "The place %(name)s was updated successfully."


@login_required
def manage_client_places(request):
    if not request.user.is_approved: raise PermissionDenied()

    client = request.user.client
    PlaceInlineFormSet = inlineformset_factory(
        Client, Place,
        fields=('name', 'description'),
        extra=0,
    )
    formset = PlaceInlineFormSet(instance=client)

    if request.method == 'POST':
        formset = PlaceInlineFormSet(request.POST, instance=client)
        if formset.is_valid():
            formset.save()
            messages.success(request, "The places were updated successfully.")
            return redirect(reverse('cis:manage_client_places'))

    return render(request, 'cis/manage_client_places.html', {
        'formset': formset,
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
        return CI.objects.filter(
            status=self.kwargs['status'],
            place__client=self.request.user.client
        )


class CIDetailView(UserApprovedMixin, DetailView):
    model = CI
    queryset = CI.objects.select_related('place', 'contract')

    def get_object(self, **kwargs):
        object = super().get_object(**kwargs)
        if object.place.client != self.request.user.client:
            # user authenticated but unauthorized
            raise Http404
        # user authenticated and authorized
        return object


class ManufacturerDetailView(UserApprovedMixin, DetailView):
    model = Manufacturer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['num_appliances'] = Appliance.objects.filter(
            manufacturer=context['manufacturer'],
            client=self.request.user,
        ).count()
        return context


class ApplianceListView(UserApprovedMixin, ListView):
    model = Appliance
    paginate_by = 10

    def get_queryset(self):
        return Appliance.objects.filter(client=self.request.user.client)


class ApplianceCreateView(UserApprovedMixin, SuccessMessageMixin, AddClientMixin, CreateView):
    model = Appliance
    form_class = ApplianceForm
    success_message = "The appliance %(serial_number)s was created successfully."


class ApplianceUpdateView(UserApprovedMixin, SuccessMessageMixin, UpdateView):
    model = Appliance
    form_class = ApplianceForm
    queryset = Appliance.objects.select_related('client', 'manufacturer')
    success_message = "The appliance was updated successfully."


@login_required
def ci_upload(request):
    if not request.user.is_approved: raise PermissionDenied()

    result = None
    form = UploadCIsForm()

    if request.method == 'POST':
        form = UploadCIsForm(request.POST, request.FILES)
        if form.is_valid():
            result = CILoader(request.FILES['file']).save()

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
            pack.send_to_production(ci_pks)
            messages.success(request, 'Pack created.')
        except DatabaseError:
            raise DatabaseError('There was an error during the sending of the CIs to production.')

    return render(request, 'homepage.html')
