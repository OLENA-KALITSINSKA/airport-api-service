from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Ticket,
    Order,
    TicketClass, Airline
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ["name", "logo"]


class AirlineImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ["id", "logo"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "total_seats",
            "airplane_type",
            "airline"
        ]


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    airline_logo = serializers.ImageField(
        source="airline.logo",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "total_seats",
            "airline_logo",
            "airplane_type"
        )


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer()
    airline = AirlineSerializer()


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "full_name", "position"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "duration"
        ]


class FlightListSerializer(FlightSerializer):
    crew = CrewSerializer(many=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "duration",
            "tickets_available"
        ]


class TicketClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketClass
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    ticket_class = serializers.SlugRelatedField(
        queryset=TicketClass.objects.all(),
        slug_field='name'
    )

    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "ticket_class"]


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(FlightSerializer):
    crew = CrewSerializer(many=True)
    airplane = AirplaneSerializer()
    route = RouteSerializer()
    taken_places = TicketSeatsSerializer(
        source="tickets",
        many=True,
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
            "taken_places"
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def validate(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one ticket is required."
            )
        return value

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
