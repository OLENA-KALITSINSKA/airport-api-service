from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, mixins
from django.db.models import F, Count
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated


from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    TicketClass,
)
from .serializers import (
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    FlightListSerializer,
    OrderListSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    FlightDetailSerializer,
    TicketClassSerializer
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class TicketClassViewSet(viewsets.ModelViewSet):
    queryset = TicketClass.objects.all()
    serializer_class = TicketClassSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related('source', 'destination').all()
    serializer_class = RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("airplane_type")

        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related('airplane', 'route')
        .prefetch_related('crew')
        .annotate(
            tickets_available=(
                F('airplane__rows') * F('airplane__seats_in_row')
                - Count('tickets')
            )
        )
    )

    serializer_class = FlightListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    def get_queryset(self):
        departure_date = self.request.query_params.get("departure_date")
        airplane_id_str = self.request.query_params.get("airplane")
        route_id_str = self.request.query_params.get("route")

        queryset = self.queryset

        if departure_date:
            departure_date = datetime.strptime(
                departure_date,
                "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(departure_time__date=departure_date)

        if airplane_id_str:
            queryset = queryset.filter(airplane_id=int(airplane_id_str))

        if route_id_str:
            queryset = queryset.filter(route_id=int(route_id_str))

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure_date",
                type=OpenApiTypes.DATE,
                description="Filter by departure date "
                            "(ex. ?departure_date=2024-09-01)",
            ),
            OpenApiParameter(
                "airplane",
                type=OpenApiTypes.INT,
                description="Filter by airplane id (ex. ?airplane=1)",
            ),
            OpenApiParameter(
                "route",
                type=OpenApiTypes.INT,
                description="Filter by route id (ex. ?route=3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.none()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            "user"
        ).prefetch_related(
            "tickets__flight__airplane",
            "tickets__flight__route"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
