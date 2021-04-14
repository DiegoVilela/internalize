from django.contrib import admin
from django.db import DatabaseError, transaction
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Client, Place, ISP, Circuit,
    CI, Manufacturer, Appliance, Contract, CIPack
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'view_places')
    search_fields = ('name', 'place__name')
    view_on_site = False

    @admin.display(description='Places')
    def view_places(self, obj):
        places = obj.place_set.all()
        places_link_list = ['<ul>']
        for place in places:
            url = f'{reverse("admin:cis_place_change", args={place.pk})}'
            safe_link = format_html('<a href="{}">{}</a>', url, place.name)
            places_link_list.append(f'<li>{safe_link}</li>')
        places_link_list.append('</ul>')
        return mark_safe('\n'.join(places_link_list))


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_link', 'description')
    list_filter = ('client',)
    list_editable = ('description',)
    search_fields = ('name', 'client__name', 'description')

    @admin.display(description='Client', ordering='client__name')
    def client_link(self, obj):
        url = f'{reverse("admin:cis_client_change", args={obj.client.pk})}'
        return format_html('<a href="{}">{}</a>', url, obj.client.name)


@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number',
        'client',
        'manufacturer',
        'model',
        'virtual',
    )
    list_filter = ('client', 'manufacturer', 'virtual')
    list_editable = ('model', 'virtual')
    search_fields = ('serial_number', 'model', 'client__name', 'manufacturer__name')
    autocomplete_fields = ('client', 'manufacturer')


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'view_appliances')
    search_fields = ('name',)

    @admin.display(description='Appliances')
    def view_appliances(self, obj):
        count = obj.appliance_set.count()
        url = f'{reverse("admin:cis_appliance_changelist")}?manufacturer__id__exact={obj.pk}'
        return format_html('<a href="{}">{} Appliances</a>', url, count)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    date_hierarchy = 'begin'
    list_display = ('name', 'begin', 'end', 'description')
    list_editable = ('begin', 'end', 'description')
    list_filter = ('begin', 'end')
    search_fields = ('name', 'description', 'begin', 'end')


@admin.action(description='Mark selected CIs as approved')
def approve_selected_cis(modeladmin, request, queryset: QuerySet):
    # todo Write test
    try:
        with transaction.atomic():
            queryset.update(status=2)
            CIPack.objects.update_approver(request.user, queryset)
    except DatabaseError:
        raise DatabaseError('There was an error during the approval of CIs.')


@admin.register(CI)
class CIAdmin(admin.ModelAdmin):
    list_display = (
        'hostname',
        'client',
        'view_place_name',
        'ip',
        'description',
        'deployed',
        'business_impact',
        'contract',
        'status',
        'view_appliances',
        'pack',
    )
    list_filter = ('status', 'client__name', 'place', 'deployed', 'contract')
    actions = [approve_selected_cis]
    readonly_fields = ('status',)
    fieldsets = (
        ('Client', {'fields': ((), ('client', 'place',))}),
        ('Configuration Item', {'fields': (
            'appliances',
            ('hostname', 'ip', 'deployed'),
            ('description', 'business_impact'),
        )}),
        ('Contract', {'fields': ('contract',)}),
        ('Credentials', {
            'fields': (
                (),
                ('username', 'password', 'enable_password', 'instructions')),
            'classes': ('collapse',),
        }),
        ('Management', {
            'fields': ('status',),
        })
    )
    filter_horizontal = ('appliances',)
    list_editable = (
        'ip',
        'description',
        'deployed',
        'business_impact',
    )
    list_select_related = ('contract', 'client', 'place', 'pack')

    @admin.display(description='Appliances')
    def view_appliances(self, obj):
        count = obj.appliances.count()
        url = f'{reverse("admin:cis_appliance_changelist")}?ci__exact={obj.pk}'
        return format_html('<a href="{}">{} Appliances</a>', url, count)

    @admin.display(description='Place')
    def view_place_name(self, obj):
        return obj.place.name


@admin.register(CIPack)
class CIPackAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'responsible', 'percentage_of_cis_approved', 'approved_by')
    list_filter = ('responsible', 'sent_at')
    readonly_fields = ('responsible', 'percentage_of_cis_approved', 'sent_at')


# admin.site.register(ISP)
# admin.site.register(Circuit)
