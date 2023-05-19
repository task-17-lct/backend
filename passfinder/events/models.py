from django.contrib.postgres.fields import ArrayField
from django.db import models
from location_field.models.plain import PlainLocationField
from polymorphic.models import PolymorphicModel


class OIDModel(models.Model):
    oid = models.CharField(primary_key=True, max_length=24)

    class Meta:
        abstract = True


class Region(OIDModel):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class Country(OIDModel):
    title = models.CharField(max_length=250)

    def __str__(self):
        return self.title


class City(OIDModel):
    title = models.CharField(max_length=250)
    region = models.ForeignKey(
        "Region", related_name="cities", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title


class Place(OIDModel):
    address = models.CharField(max_length=250)
    parser_source = models.CharField(max_length=250)
    city = models.ForeignKey(
        "City", related_name="places", null=True, on_delete=models.SET_NULL
    )
    description = models.TextField()
    location = PlainLocationField(zoom=6)
    sites = ArrayField(models.CharField(max_length=250))
    phones = ArrayField(models.CharField(max_length=250))
    working_time = models.JSONField(null=True)


class Tag(OIDModel):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class BasePoint(OIDModel, PolymorphicModel):
    title = models.CharField(max_length=250)
    parser_source = models.CharField(max_length=250)
    description = models.TextField()
    city = models.ForeignKey(
        "City", related_name="points", null=True, on_delete=models.SET_NULL
    )
    region = models.ForeignKey(
        "Region", related_name="points", null=True, on_delete=models.SET_NULL
    )
    creator = models.CharField(max_length=250)
    partner = models.CharField(max_length=250)
    payment_method = models.CharField(max_length=250)
    # tags = models.ManyToManyField("Tag", related_name="points")

    def __str__(self):
        return self.title


class PointMedia(OIDModel):
    file = models.FileField(upload_to="uploads/")
    type = models.CharField(max_length=200)
    point = models.ForeignKey(
        "BasePoint", related_name="media", on_delete=models.CASCADE
    )


class Event(BasePoint):
    ya_id = models.CharField(blank=True, max_length=24)
    age = models.CharField("Возрастное ограничение", max_length=50)
    booking_link = models.URLField()
    discover_moscow_link = models.URLField()
    duration = models.IntegerField(blank=True, null=True)
    ticket_price = models.IntegerField(blank=True, null=True)
    schedule = models.JSONField(null=True)


class Hotel(BasePoint):
    address = models.CharField(max_length=250)
    location = PlainLocationField(zoom=6)
    rooms = models.JSONField(null=True)
    email = models.CharField(max_length=250)
    stars = models.IntegerField(null=True)


class HotelPhone(models.Model):
    hotel = models.ForeignKey("Hotel", related_name="phones", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=18)


class Museum(BasePoint):
    # TODO
    ...


class Excursion(BasePoint):
    duration_hours = models.IntegerField()
    price = models.IntegerField()
    minGroupCount = models.CharField(max_length=250)
    program = models.TextField()


class ExcursionRoute(models.Model):
    excursion = models.ForeignKey(
        "Excursion", related_name="routes", on_delete=models.CASCADE
    )
    point = models.ForeignKey("Event", related_name="routes", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class Restaurant(BasePoint):
    bill = models.IntegerField()
    avg_time_visit = models.IntegerField()
    can_reserve = models.BooleanField()
    working_time = models.JSONField(null=True)
    location = PlainLocationField(zoom=6)
    phone = models.CharField(max_length=18)
