from django.db import models
from django.conf import settings


# Create your models here.
class Airport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey("Airport",
                               on_delete=models.CASCADE,
                               related_name="departing_routes")
    destination = models.ForeignKey("Airport",
                                      on_delete=models.CASCADE,
                                    related_name='arriving_routes')
    distance = models.IntegerField()

    def __str__(self):
        return (f"Route from {self.source.name} to "
                f"{self.destination.name} ({self.distance} km)")


class Crew(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class AirplaneType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey("AirplaneType", on_delete=models.CASCADE)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Flight(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey("Route", on_delete=models.CASCADE)
    airplane = models.ForeignKey("Airplane", on_delete=models.CASCADE)
    crew = models.ManyToManyField("Crew", blank=True)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (f"Flight {self.route} on"
                f" {self.departure_time.strftime('%Y-%m-%d %H:%M')}")


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name="orders"
    # )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
