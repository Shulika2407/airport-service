from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from airport.serializers import (AirportSerializer,
                                 RouteSerializer,
                                 RouteDetailSerializer,
                                 RouteListSerializer,
                                 CrewSerializer,
                                 AirplaneTypeSerializer,
                                 AirplaneSerializer,
                                 FlightSerializer, FlightListSerializer,
                                 FlightDetailSerializer,
                                 OrderSerializer, OrderListSerializer)

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from airport.models import (Airport, Route,
                     Crew, AirplaneType,
                     Airplane, Flight,
                     Order, Ticket)
# Create your views here.


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer


    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.order_by("id")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related("route",
                                             "route__source",
                                             "route__destination",
                                             "airplane",
                                             "airplane__airplane_type"
                                             ).prefetch_related("crew").order_by("id")
    serializer_class = FlightSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        airplane_name = self.request.query_params.get("airplane_name")
        crew = self.request.query_params.get("crew")
        queryset = self.queryset

        if airplane_name:
            queryset = queryset.filter(airplane__name__icontains=airplane_name)

        if crew:
            crew_ids = self._params_to_ints(crew)
            queryset = queryset.filter(crew__id__in=crew_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane_name",
                type=str,
                description="Filter by airplane",
                required=False,
            ),
            OpenApiParameter(
                "crew",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by crew id (ex. ?crew=1,2)",

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("tickets__flight__route__source",
                                              "tickets__flight__route__destination",
                                              "tickets__flight__airplane__airplane_type",
                                              "tickets__flight__crew").order_by("id")
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

