# Generated by Django 4.0.4 on 2024-09-10 08:15

import airport.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Airline",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("name", models.CharField(max_length=100)),
                ("logo", models.ImageField(
                    null=True,
                    upload_to=airport.models.airline_image_file_path
                )),
            ],
        ),
        migrations.CreateModel(
            name="Airplane",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("name", models.CharField(max_length=100)),
                ("rows", models.IntegerField()),
                ("seats_in_row", models.IntegerField()),
                ("airline", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to="airport.airline"
                )),
            ],
        ),
        migrations.CreateModel(
            name="AirplaneType",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Airport",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("name", models.CharField(max_length=100)),
                ("closest_big_city", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Crew",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("position", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TicketClass",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("name", models.CharField(
                    choices=[
                        ("economy", "Economy"),
                        ("business", "Business"),
                        ("first_class", "First Class"),
                        ("premium_economy", "Premium Economy")
                    ],
                    max_length=20,
                    unique=True
                )),
                ("price_multiplier", models.FloatField(default=1.0)),
                ("baggage_allowance", models.IntegerField(default=20)),
                ("cancellation_policy", models.TextField()),
                ("meal_service", models.BooleanField(default=False)),
                ("priority_boarding", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Route",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("distance", models.IntegerField()),
                ("destination", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="arriving_routes",
                    to="airport.airport"
                )),
                ("source", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="departing_routes",
                    to="airport.airport"
                )),
            ],
        ),
        migrations.CreateModel(
            name="Flight",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("departure_time", models.DateTimeField()),
                ("arrival_time", models.DateTimeField()),
                ("airplane", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to="airport.airplane"
                )),
                ("crew", models.ManyToManyField(
                    related_name="flights",
                    to="airport.crew"
                )),
                ("route", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to="airport.route"
                )),
            ],
            options={
                "ordering": ["-arrival_time"],
            },
        ),
        migrations.AddField(
            model_name="airplane",
            name="airplane_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="airport.airplanetype"
            ),
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name="ID"
                )),
                ("row", models.IntegerField()),
                ("seat", models.IntegerField()),
                ("flight", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="tickets",
                    to="airport.flight"
                )),
                ("order", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="tickets",
                    to="airport.order"
                )),
                ("ticket_class", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to="airport.ticketclass"
                )),
            ],
            options={
                "ordering": ["row", "seat"],
                "unique_together": {("flight", "row", "seat")},
            },
        ),
    ]
