import os
import uuid

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.name} to {self.destination.name}"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError(
                "Source and destination airports cannot be the same."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


def airline_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}.{extension}"
    return os.path.join("uploads/airplanes/", filename)


class Airline(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(null=True, upload_to=airline_image_file_path)

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    airline = models.ForeignKey(
        Airline,
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    @property
    def total_seats(self):
        return self.rows * self.seats_in_row


class Crew(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}: {self.position}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    def __str__(self):
        return f"Flight on {self.route} at {self.departure_time}"

    class Meta:
        ordering = ["-arrival_time"]

    @property
    def duration(self):
        delta = self.arrival_time - self.departure_time
        return delta.total_seconds() / 60

    def clean(self):
        if self.arrival_time <= self.departure_time:
            raise ValidationError(
                "Arrival time must be later than departure time."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Order {self.id} by {self.user}"

    class Meta:
        ordering = ["-created_at"]


class TicketClass(models.Model):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST_CLASS = "first_class"
    PREMIUM_ECONOMY = "premium_economy"

    TICKET_CLASS_CHOICES = [
        (ECONOMY, "Economy"),
        (BUSINESS, "Business"),
        (FIRST_CLASS, "First Class"),
        (PREMIUM_ECONOMY, "Premium Economy"),
    ]

    name = models.CharField(
        max_length=20,
        choices=TICKET_CLASS_CHOICES,
        unique=True
    )
    price_multiplier = models.FloatField(default=1.0)
    baggage_allowance = models.IntegerField(default=20)
    cancellation_policy = models.TextField()
    meal_service = models.BooleanField(default=False)
    priority_boarding = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    ticket_class = models.ForeignKey(
        TicketClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {airplane_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"Ticket {self.row}-{self.seat} on {self.flight}"

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
