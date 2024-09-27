from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    TicketClassViewSet,
    AirlineViewSet,
)

router = DefaultRouter()
router.register("airports", AirportViewSet)
router.register("ticket_class", TicketClassViewSet)
router.register("routes", RouteViewSet)
router.register("airlines", AirlineViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("crews", CrewViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
