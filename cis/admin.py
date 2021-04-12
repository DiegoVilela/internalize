from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Client, Place, ISP, Circuit,
    CI, Manufacturer, Appliance, Contract, CIPack
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'client')


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


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('name', 'begin', 'end', 'description')
    list_filter = ('begin', 'end')
    search_fields = ('name',)


@admin.action(description='Mark selected CIs as approved')
def approve_selected_cis(modeladmin, request, queryset):
    queryset.update(status=2)
    # todo Dispatch a signal to update the CIPack approved percentage.


@admin.register(CI)
class CIAdmin(admin.ModelAdmin):
    list_display = (
        'hostname',
        'place',
        'ip',
        'description',
        'view_appliances',
        'deployed',
        'business_impact',
        'status',
        'contract',

    )
    list_filter = ('status', 'client__name', 'place', 'deployed', 'contract')
    readonly_fields = ('status',)
    actions = [approve_selected_cis]

    def view_appliances(self, obj):
        count = obj.appliances.count()
        url = f'{reverse("admin:cis_appliance_changelist")}?ci__exact={obj.pk}'
        return format_html('<a href="{}">{} Appliances</a>', url, count)


@admin.register(CIPack)
class CIPackAdmin(admin.ModelAdmin):
    list_display = ('id', 'responsible', 'sent_at', 'approved')
    list_filter = ('responsible', 'approved', 'sent_at')
    readonly_fields = ('responsible', 'approved', 'sent_at')
    raw_id_fields = ('items',)


admin.site.register(ISP)
admin.site.register(Circuit)
