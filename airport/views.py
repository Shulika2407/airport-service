from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from airport.serializers import (AirportSerializer,
                                 RouteSerializer,
                                 RouteDetailSerializer,
                                 RouteListSerializer,
                                 CrewSerializer,
                                 AirplaneTypeSerializer,
                                 AirplaneTypeImageSerializer,
                                 AirplaneTypeDetail,
                                 AirplaneSerializer,
                                 FlightSerializer, FlightListSerializer,
                                 FlightDetailSerializer,
                                 OrderSerializer, OrderListSerializer)

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import F, Count
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from airport.models import (Airport, Route,
                     Crew, AirplaneType,
                     Airplane, Flight,
                     Order, Ticket)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
# Create your views here.


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirplaneTypeImageSerializer

        if self.action == "retrieve":
            return AirplaneTypeDetail

        return AirplaneTypeSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        airplane_type = self.get_object()
        serializer = self.get_serializer(airplane_type, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
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
    ).order_by("id")

    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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


class OrderPagination(PageNumberPagination):
    page_size = 2
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (Order.objects
                .select_related("customer")
                .prefetch_related("tickets__flight__route__source",
                                  "tickets__flight__route__destination",
                                  "tickets__flight__airplane__airplane_type",
                                  "tickets__flight__crew").order_by("-created_at"))

    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

