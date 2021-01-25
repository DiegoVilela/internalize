from django.contrib import admin
from .models import (
    Client,
    Site,
    ISP,
    Manufacturer,
    Circuit,
    Contract,
    Appliance,
    Setup,
    Credential,
    CI
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
