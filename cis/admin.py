from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.db import DatabaseError, transaction
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ngettext

from .models import (
    Client, Place, ISP, Circuit,
    CI, Manufacturer, Appliance, Contract, CIPack
)


SITE = 'Internalize'
AdminSite.site_header = SITE
AdminSite.site_title = SITE


class ClientLinkMixin:
    """Add the Client name as a link"""

    @admin.display(description='Client', ordering='client__name')
    def client_link(self, obj):
        url = f'{reverse("admin:cis_client_change", args={obj.client.pk})}'
        return format_html('<a href="{}">{}</a>', url, obj.client.name)


class PlaceInline(admin.TabularInline):
    model = Place
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'view_places')
    search_fields = ('name', 'place__name')
    view_on_site = False
    inlines = (PlaceInline,)

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


class CIInline(admin.TabularInline):
    model = CI
    extra = 0
    max_num = 0  # prevents the link `add another` from appearing
    fields = ('description', 'deployed', 'business_impact', 'contract', 'status', 'pack')
    readonly_fields = ('description', 'deployed', 'business_impact', 'contract', 'status', 'pack')
    show_change_link = True


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin, ClientLinkMixin):
    list_display = ('name', 'client_link', 'description')
    list_filter = ('client',)
    list_editable = ('description',)
    search_fields = ('name', 'client__name', 'description')
    inlines = (CIInline,)


@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin, ClientLinkMixin):
    list_display = (
        'serial_number',
        'client_link',
        'manufacturer_link',
        'model',
        'virtual',
    )
    list_filter = ('client', 'manufacturer', 'virtual')
    list_editable = ('model', 'virtual')
    search_fields = ('serial_number', 'model', 'client__name', 'manufacturer__name')
    autocomplete_fields = ('client', 'manufacturer')

    @admin.display(description='Manufacturer', ordering='manufacturer__name')
    def manufacturer_link(self, obj):
        url = f'{reverse("admin:cis_manufacturer_change", args={obj.manufacturer.pk})}'
        return format_html('<a href="{}">{}</a>', url, obj.manufacturer.name)


class ApplianceInline(admin.TabularInline):
    model = Appliance
    extra = 1


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'view_appliances')
    search_fields = ('name',)
    inlines = (ApplianceInline,)

    @admin.display(description='Appliances')
    def view_appliances(self, obj):
        count = obj.appliance_set.count()
        url = f'{reverse("admin:cis_appliance_changelist")}?manufacturer__id__exact={obj.pk}'
        return format_html('<a href="{}">{} Appliances</a>', url, count)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    FIELDS = ('name', 'begin', 'end', 'description')

    date_hierarchy = 'begin'
    list_display = FIELDS
    list_filter = ('begin', 'end')
    search_fields = FIELDS
    inlines = (CIInline,)


@admin.register(CI)
class CIAdmin(admin.ModelAdmin, ClientLinkMixin):
    list_display = (
        'hostname',
        'client_link',
        'place_link',
        'ip',
        'description',
        'deployed',
        'business_impact',
        'contract',
        'status',
        'view_appliances',
        'pack',
    )
    list_filter = ('pack', 'status', 'client__name', 'place', 'deployed', 'contract')
    actions = ['approve_selected_cis']
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

    @admin.display(description='Place', ordering='place__name')
    def place_link(self, obj):
        url = f'{reverse("admin:cis_place_change", args={obj.place.pk})}'
        return format_html('<a href="{}">{}</a>', url, obj.place.name)

    @admin.display(description='Appliances')
    def view_appliances(self, obj):
        count = obj.appliances.count()
        url = f'{reverse("admin:cis_appliance_changelist")}?ci__exact={obj.pk}'
        return format_html('<a href="{}">{} Appliances</a>', url, count)

    @admin.action(description='Mark selected CIs as approved')
    def approve_selected_cis(self, request, queryset: QuerySet):
        # todo Write test
        pack_ids = set(queryset.values_list('pack', flat=True))
        try:
            with transaction.atomic():
                count = queryset.update(status=2)
                CIPack.objects.filter(pk__in=pack_ids).update(approved_by=request.user)
            self.message_user(
                request,
                ngettext(
                    'The selected CI was approved successfully.',
                    'The selected CIs were approved successfully.',
                    count
                ),
                level=messages.SUCCESS,
            )
        except DatabaseError as e:
            raise DatabaseError(f'An error occurred during the approval: {e}')


@admin.register(CIPack)
class CIPackAdmin(admin.ModelAdmin):
    FIELDS = ('sent_at', 'responsible', 'percentage_of_cis_approved', 'approved_by')

    list_display = FIELDS
    list_filter = ('responsible', 'sent_at', 'approved_by')
    readonly_fields = FIELDS
    inlines = (CIInline,)

# admin.site.register(ISP)
# admin.site.register(Circuit)
