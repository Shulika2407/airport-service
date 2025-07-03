import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from django.db.models import F, Count
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from airport.models import (Route, Airport,
                           Crew, Airplane, AirplaneType,
                           Flight, Ticket, Order)

from airport.tests.test_utils import (sample_airport,
                                      sample_route, sample_crew,
                                      sample_airplane_type, sample_airplane,
                                      sample_flight, sample_order, sample_ticket)

from airport.serializers import FlightDetailSerializer, FlightListSerializer

Flight_URL = reverse("airport:flight-list")

def detail_url(flight_id):
    return reverse ("airport:flight-detail", args=[flight_id])

class UnauthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(Flight_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def _get_annotated_flight_queryset(flight_id=None):
    queryset = Flight.objects.select_related(
        "route",
        "route__source",
        "route__destination",
        "airplane",
        "airplane__airplane_type"
    ).prefetch_related(
        "crew"
    ).annotate(
        tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
        )
    )
    if flight_id is not None:
        return queryset.filter(id=flight_id)
    return queryset

class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)
        self.maxDiff = None
        self.airport1 = sample_airport(name="AirportA")
        self.airport2 = sample_airport(name="AirportB")
        self.route = sample_route(self.airport1, self.airport2)
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane(self.airplane_type, name="TestPlane", rows=10, seats_in_row=5)
        self.crew1 = sample_crew(first_name="John", last_name="Doe")
        self.crew2 = sample_crew(first_name="Jane", last_name="Smith")

    def test_filter_flight_by_airplane_name(self):
        airplane1 = sample_airplane(self.airplane_type, name="UR-BAA",
                                    rows=10, seats_in_row=5)
        airplane2 = sample_airplane(self.airplane_type, name="UR-BAB",
                                    rows=10, seats_in_row=5)

        flight1 = sample_flight(self.route, airplane1, crew_list=[self.crew1])
        flight2 = sample_flight(self.route, airplane2, crew_list=[self.crew2])


        res = self.client.get(Flight_URL + "?airplane_name=UR-BAA")

        serializer_data_expected = FlightListSerializer(
            _get_annotated_flight_queryset(flight_id=flight1.id).first()).data
        serializer_data_not_expected = FlightListSerializer(
            _get_annotated_flight_queryset(flight_id=flight2.id).first()).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictEqual(serializer_data_expected, res.data[0])
        self.assertNotIn(serializer_data_not_expected, res.data)

    def test_flight_list(self):
        sample_flight(self.route, self.airplane, crew_list=[self.crew1])
        sample_flight(self.route, self.airplane, crew_list=[self.crew2])

        res = self.client.get(Flight_URL)
        flights_queryset_for_test = _get_annotated_flight_queryset().order_by("id")
        serializer = FlightListSerializer(flights_queryset_for_test, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_flight_by_crew(self):
        crew1 = sample_crew(first_name="Crew 1", last_name="Last 1")
        crew2 = sample_crew(first_name="Crew 2", last_name="Last 2")
        crew3_for_test = sample_crew(first_name="TestCrew3", last_name="Last3")

        flight1 = sample_flight(self.route, self.airplane, crew_list=[crew1])
        flight2 = sample_flight(self.route, self.airplane, crew_list=[crew2])
        flight3 = sample_flight(self.route, self.airplane, crew_list=[crew3_for_test])

        # flight1.crew.add(crew1)
        # flight2.crew.add(crew2)


        res = self.client.get(
            Flight_URL, {"crew": f"{crew1.id},{crew2.id}"}
        )

        serializer_data_expected = FlightListSerializer(
            _get_annotated_flight_queryset(flight_id=flight1.id).first()).data
        serializer_data_expected2 = FlightListSerializer(
            _get_annotated_flight_queryset(flight_id=flight2.id).first()).data
        serializer_data_not_expected = FlightListSerializer(
            _get_annotated_flight_queryset(flight_id=flight3.id).first()).data

        self.assertIn(serializer_data_expected, res.data)
        self.assertIn(serializer_data_expected2, res.data)
        self.assertNotIn(serializer_data_not_expected, res.data)

    def test_retrieve_list(self):
        flight = sample_flight(self.route, self.airplane, crew_list=[self.crew1])
        url = detail_url(flight.id)
        res = self.client.get(url)
        serializer = FlightDetailSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
