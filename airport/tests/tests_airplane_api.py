import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from airport.models import Airplane, AirplaneType, Airline
from airport.serializers import AirplaneListSerializer, AirplaneRetrieveSerializer

AIRPLANE_URL = reverse("airport:airplane-list")
AIRLINE_URL = reverse("airport:airline-list")


def sample_airline(**params):
    defaults = {
        "name": "Sample airline"
    }
    defaults.update(params)

    return Airline.objects.create(**defaults)


def sample_airplane(**params) -> Airplane:
    airplane_type = AirplaneType.objects.create(name="test_type")
    defaults = {
        "name": "Sample name",
        "rows": 10,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
        "airline": None
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def image_upload_url(airline_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airline-upload-image", args=[airline_id])


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        sample_airplane()
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.order_by("id")
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_airplanes_by_name(self):
        airplane1 = sample_airplane()
        airplane2 = sample_airplane()
        sample_airplane(name="Not match")

        response = self.client.get(AIRPLANE_URL, {"name": "name"})

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertEqual(len(response.data), 2)

    def test_filter_airplanes_by_airplane_type(self):
        airplane_type1 = AirplaneType.objects.create(name="Type A")
        airplane_type2 = AirplaneType.objects.create(name="Type B")

        airplane1 = sample_airplane(airplane_type=airplane_type1)
        sample_airplane(airplane_type=airplane_type1)

        response = self.client.get(AIRPLANE_URL, {"airplane_type": "Type A"})

        serializer1 = AirplaneListSerializer(airplane1)

        self.assertIn(serializer1.data, response.data)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_airplane_detail(self):
        airplane_type = AirplaneType.objects.create(name="Test Type")
        airplane = sample_airplane(airplane_type=airplane_type)

        url = reverse("airport:airplane-detail", args=[airplane.id])
        res = self.client.get(url)

        serializer = AirplaneRetrieveSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        airplane_type = AirplaneType.objects.create(name="Test Type")
        payload = {
            "name": "Test Airplane",
            "rows": 10,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(name="Test Type")
        payload = {
            "name": "Test Airplane",
            "rows": 10,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class AirlineImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airline = sample_airline()
        self.airplane = sample_airplane(airline=self.airline)

    def tearDown(self):
        self.airline.logo.delete()

    def test_upload_image_to_airline(self):
        url = image_upload_url(self.airline.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"logo": ntf}, format="multipart")
        self.airline.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("logo", res.data)
        self.assertTrue(os.path.exists(self.airline.logo.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airline.id)
        res = self.client.post(url, {"logo": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_url_is_shown_on_airline_list(self):
        url = image_upload_url(self.airline.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"logo": ntf}, format="multipart")
        res = self.client.get(AIRLINE_URL)

        self.assertIn("logo", res.data[0].keys())

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airline.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"logo": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("airline_logo", res.data[0].keys())
