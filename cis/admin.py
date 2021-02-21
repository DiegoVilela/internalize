from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _

from .models import (
    User, Client, Site, ISP, Circuit,
    CI, Manufacturer, Appliance, Setup, Contract, Credential, CIPack
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Client'), {'fields': ('client',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(Client)
admin.site.register(Site)
admin.site.register(ISP)
admin.site.register(Manufacturer)
admin.site.register(Circuit)
admin.site.register(Contract)
admin.site.register(Appliance)
admin.site.register(Setup)
admin.site.register(Credential)
admin.site.register(CI)
admin.site.register(CIPack)
