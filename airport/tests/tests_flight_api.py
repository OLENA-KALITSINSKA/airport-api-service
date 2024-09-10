from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Crew, Route, Flight
from airport.serializers import FlightListSerializer
from airport.tests.tests_airplane_api import sample_airplane
from airport.tests.tests_airport_api import sample_airport

CREW_URL = reverse("airport:crew-list")
FLIGHT_URL = reverse("airport:flight-list")
ROUTES_URL = reverse("airport:route-list")


def get_detail_flight_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


def sample_route(**params):
    source_airport = sample_airport()
    destination_airport = sample_airport()

    defaults = {
        "source": source_airport,
        "destination": destination_airport,
        "distance": 1000
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": "test name",
        "last_name": "test last name",
        "position": "pilot"
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_time():
    future_time = datetime.now() + timedelta(days=1)
    return future_time


def sample_flight():
    departure_time = sample_time()
    route = sample_route()
    airplane = sample_airplane()
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=departure_time,
        arrival_time=(departure_time + timedelta(hours=2)),
    )
    return flight


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_auth_required(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

        self.airplane = sample_airplane()
        self.route = sample_route()
        self.flight1 = sample_flight()

    def test_list_flights(self):
        sample_flight()
        sample_flight()
        sample_flight()

        response = self.client.get(FLIGHT_URL)
        data = response.data
        for flight in data:
            del flight["tickets_available"]

        flights = Flight.objects.order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, serializer.data)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()
        departure_time = sample_time()
        data = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure_time,
            "arrival_time": (departure_time + timedelta(hours=2)),
        }
        response = self.client.post(FLIGHT_URL, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_departure_date(self):
        date_str = self.flight1.departure_time.date().isoformat()
        response = self.client.get(FLIGHT_URL, {"departure_date": date_str})
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(flight["departure_time"]
                .startswith(date_str) for flight in data)
        )

    def test_filter_by_airplane(self):
        self.airplane = sample_airplane()
        response = self.client.get(
            FLIGHT_URL, {"airplane": self.airplane.id}
        )
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(flight["airplane"] == self.airplane.id for flight in data)
        )

    def test_filter_by_route(self):
        response = self.client.get(FLIGHT_URL, {"route": self.route.id})
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(flight["route"] == self.route.id for flight in data)
        )

    def test_filter_by_multiple_params(self):
        departure_date = self.flight1.departure_time.date()
        response = self.client.get(FLIGHT_URL, {
            "departure_date": departure_date,
            "airplane": self.airplane.id,
            "route": self.route.id
        })
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(flight["departure_time"]
                .startswith(departure_date) for flight in data)
        )
        self.assertTrue(
            all(flight["airplane"] == self.airplane.id for flight in data)
        )
        self.assertTrue(
            all(flight["route"] == self.route.id for flight in data)
        )


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.route = sample_route()
        self.airplane = sample_airplane()
        self.crew_member_1 = sample_crew()
        self.crew_member_2 = sample_crew()

    def test_create_flight(self):
        departure_time = sample_time()
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": departure_time,
            "arrival_time": (departure_time + timedelta(hours=2)),
            "crew": [self.crew_member_1.id, self.crew_member_2.id]
        }

        response = self.client.post(FLIGHT_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_flight(self):
        flight = sample_flight()
        departure_time = sample_time()
        data = {
            "departure_time": departure_time,
        }

        url = get_detail_flight_url(flight_id=flight.id)
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_flight(self):
        flight = sample_flight()
        departure_time = sample_time()
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": departure_time,
            "arrival_time": (departure_time + timedelta(hours=2)),
            "crew": [self.crew_member_1.id, self.crew_member_2.id]
        }

        url = get_detail_flight_url(flight_id=flight.id)
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_flight(self):
        flight = sample_flight()

        url = get_detail_flight_url(flight_id=flight.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_crew(self):
        data = {
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "position": "Pilot"
        }
        response = self.client.post(CREW_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
