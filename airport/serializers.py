from rest_framework import serializers
from .models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Ticket,
    Order
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


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "total_seats", "airplane_type"]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = AirplaneSerializer()
    crew = CrewSerializer(many=True)

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crew", "duration"]


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user", "tickets"]
