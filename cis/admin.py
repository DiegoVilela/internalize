from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User, Client, Site, ISP, Circuit,
    CI, Manufacturer, Appliance, Setup, Contract, Credential
)

admin.site.register(User, UserAdmin)
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
