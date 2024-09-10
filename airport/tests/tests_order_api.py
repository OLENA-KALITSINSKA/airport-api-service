from unittest import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from airport.models import Order, Ticket, TicketClass
from airport.serializers import OrderListSerializer
from airport.tests.tests_flight_api import sample_flight

ORDER_URL = reverse("airport:order-list")


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_order_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_order_list(self):
        flight = sample_flight()

        order_1 = Order.objects.create(user=self.user)
        order_2 = Order.objects.create(user=self.user)
        order_3 = Order.objects.create(user=self.user)
        ticket_class1 = TicketClass.objects.create(name="economy")
        ticket_class2 = TicketClass.objects.create(name="business")
        Ticket.objects.create(
            row=1,
            seat=1,
            flight=flight,
            order=order_1,
            ticket_class=ticket_class1,
        ),
        Ticket.objects.create(
            row=1,
            seat=2,
            flight=flight,
            order=order_2,
            ticket_class=ticket_class2,
        )
        Ticket.objects.create(
            row=1,
            seat=3,
            flight=flight,
            order=order_3,
            ticket_class=ticket_class1,
        )

        response = self.client.get(ORDER_URL)

        orders = Order.objects.order_by("-created_at")
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
