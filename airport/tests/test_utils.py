from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone


from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)


def sample_airport(**params):
    defaults = {
        "name": "Boryspil International Airport",
        "closest_big_city": "Test city",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(source, destination, **params):
    defaults = {"distance": 100}
    defaults.update(params)
    return Route.objects.create(source=source, destination=destination, **defaults)


def sample_crew(**params):
    defaults = {"first_name": "John", "last_name": "Snow"}
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {"name": "Boeing 737"}
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(airplane_type, **params):
    defaults = {"name": "Test plane", "rows": 50, "seats_in_row": 6}
    defaults.update(params)
    return Airplane.objects.create(airplane_type=airplane_type, **defaults)


def sample_flight(route, airplane, crew_list=None, **params):
    defaults = {
        "departure_time": timezone.now() + timedelta(days=1),
        "arrival_time": timezone.now() + timedelta(days=1, hours=3),
    }
    defaults.update(params)
    flight = Flight.objects.create(route=route, airplane=airplane, **defaults)

    if crew_list is not None:
        flight.crew.set(crew_list)

    return flight


def sample_order(customer, **params):
    defaults = {"created_at": datetime.now()}
    defaults.update(params)
    return Order.objects.create(customer=customer, **defaults)


def sample_ticket(order, flight, **params):
    defaults = {"row": 1, "seat": 1}
    defaults.update(params)
    return Ticket.objects.create(order=order, flight=flight, **defaults)
