from django.contrib import admin

from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
    TicketClass,
    Airline,
)

admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Airplane)
admin.site.register(AirplaneType)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Flight)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(TicketClass)
