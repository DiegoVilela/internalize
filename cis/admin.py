from django.contrib import admin
from .models import (
    Client, Place, ISP, Circuit,
    CI, Manufacturer, Appliance, Contract, CIPack
)


admin.site.register(Client)
admin.site.register(Place)
admin.site.register(ISP)
admin.site.register(Manufacturer)
admin.site.register(Circuit)
admin.site.register(Contract)
admin.site.register(Appliance)
admin.site.register(CI)
admin.site.register(CIPack)
