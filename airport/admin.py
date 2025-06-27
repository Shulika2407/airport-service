from django.contrib import admin
from .models import (Airport, Route,
                     Crew, AirplaneType,
                     Airplane, Flight,
                     Order, Ticket)


# Register your models here.
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Order)
admin.site.register(Ticket)