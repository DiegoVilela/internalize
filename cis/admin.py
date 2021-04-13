from django.contrib import admin
from django.db import DatabaseError
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
    list_editable = ('client', 'manufacturer', 'model', 'virtual')
    search_fields = ('serial_number', 'model', 'client__name', 'manufacturer__name')


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
    list_display = ('name', 'begin', 'end', 'description')
    list_editable = ('begin', 'end', 'description')
    list_filter = ('begin', 'end')
    search_fields = ('name', 'description', 'begin', 'end')


def _update_pack_approved_percentage(pack: CIPack):
    print(pack, 'pack')
    num_cis_in_pack = pack.ci_set.count()
    num_cis_approved = pack.ci_set.filter(status=2).count()
    pack.approved = round((num_cis_approved / num_cis_in_pack) * 100)
    pack.save()


@admin.action(description='Mark selected CIs as approved')
def approve_selected_cis(modeladmin, request, queryset: QuerySet):
    try:
        queryset.update(status=2)

        for ci in queryset.all():
            ci.pack.approved_by = request.user
            # todo Handle CIs of different packs
            _update_pack_approved_percentage(ci.pack)

    except DatabaseError:
        raise DatabaseError('There was an error during the approval of CIs.')


@admin.register(CI)
class CIAdmin(admin.ModelAdmin):
    list_display = (
        'hostname',
        'place',
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
    #readonly_fields = ('status',)
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
    )
    filter_horizontal = ('appliances',)
    list_editable = (
        'status',
        'place',
        'ip',
        'description',
        'deployed',
        'business_impact',
        'contract'
    )

    @admin.display(description='Appliances')
    def view_appliances(self, obj):
        count = obj.appliances.count()
        url = f'{reverse("admin:cis_appliance_changelist")}?ci__exact={obj.pk}'
        return format_html('<a href="{}">{} Appliances</a>', url, count)


@admin.register(CIPack)
class CIPackAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'responsible', 'approved', 'approved_by')
    list_filter = ('responsible', 'approved', 'sent_at')
    readonly_fields = ('responsible', 'approved', 'sent_at')


# admin.site.register(ISP)
# admin.site.register(Circuit)
