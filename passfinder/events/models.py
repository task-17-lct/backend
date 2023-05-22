from django.contrib.postgres.fields import ArrayField
from django.db import models
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import ListSerializer, FloatField
from polymorphic.models import PolymorphicModel
from passfinder.utils.choices import count_max_length


class OIDModel(models.Model):
    oid = models.CharField(primary_key=True, max_length=24, unique=True)

    class Meta:
        abstract = True


class Region(OIDModel):
    city = models.ForeignKey(
        "City", null=True, related_name="regions", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    description = models.TextField()
    description_title = models.CharField(max_length=250)
    description_short = models.CharField(max_length=500)
    url = models.URLField()
    showcase_cards = models.JSONField(null=True)

    def __str__(self):
        return self.title


class RegionMedia(OIDModel):
    file = models.FileField(upload_to="uploads/")
    type = models.CharField(max_length=200)
    region = models.ForeignKey("Region", related_name="media", on_delete=models.CASCADE)


class City(OIDModel):
    title = models.CharField(max_length=250)
    region = models.ForeignKey(
        "Region", related_name="cities", null=True, on_delete=models.SET_NULL
    )
    lon = models.FloatField(default=0, db_index=True)
    lat = models.FloatField(default=0, db_index=True)

    @property
    def location(self):
        return [self.lat, self.lon]

    def __str__(self):
        return self.title


class Place(OIDModel):
    address = models.CharField(max_length=250, null=True, blank=True)
    parser_source = models.CharField(max_length=250)
    city = models.ForeignKey(
        "City", related_name="places", null=True, on_delete=models.SET_NULL
    )
    region = models.ForeignKey(
        "Region", related_name="places", null=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=250)
    description = models.TextField()
    lon = models.FloatField(default=0, db_index=True)
    lat = models.FloatField(default=0, db_index=True)
    sites = ArrayField(models.CharField(max_length=250), null=True)
    phones = ArrayField(models.CharField(max_length=250), null=True)
    working_time = models.JSONField(null=True)

    @property
    def location(self):
        return [self.lat, self.lon]


class Tag(OIDModel):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class BasePoint(OIDModel, PolymorphicModel):
    title = models.CharField(max_length=250)
    parser_source = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField()
    city = models.ForeignKey(
        "City", related_name="points", null=True, on_delete=models.SET_NULL
    )
    region = models.ForeignKey(
        "Region", related_name="points", null=True, on_delete=models.SET_NULL
    )
    place = models.ForeignKey(
        "Place", related_name="points", null=True, on_delete=models.SET_NULL
    )
    sort = models.IntegerField(default=0)
    lat = models.FloatField(default=0, db_index=True)
    lon = models.FloatField(default=0, db_index=True)
    can_buy = models.BooleanField(default=True)
    priority = models.BooleanField(default=False)

    @property
    @extend_schema_field(
        field=ListSerializer(child=FloatField(), min_length=2, max_length=2)
    )
    def location(self):
        return [self.lat, self.lon]

    @property
    @extend_schema_field(field=OpenApiTypes.URI)
    def icon(self):
        # TODO: change to icon/first image
        return "https://akarpov.ru/media/uploads/files/qMO4dDfIXP.webp"

    def __str__(self):
        return self.title


class PointMedia(OIDModel):
    file = models.FileField(upload_to="uploads/")
    type = models.CharField(max_length=200)
    point = models.ForeignKey(
        "BasePoint", related_name="media", on_delete=models.CASCADE
    )


class Event(BasePoint):
    class EventType(models.TextChoices):
        yarmarka = "fair", "ярмарка"
        bulvar = "boulevard", "бульвар"
        dostoprimechatelnost = "attraction", "достопримечательность"
        excursii = "excursion", "экскурсия"
        teatr = "theatre", "театр"
        museum = "museum", "музей"
        kino = "movie", "кино"
        concert = "concert", "концерт"
        spektatli = "plays", "спектакли"

    payment_method = models.CharField(max_length=250, null=True, blank=True)
    type = models.CharField(
        db_index=True,
        choices=EventType.choices,
        max_length=count_max_length(EventType),
    )
    age = models.CharField(
        "Возрастное ограничение", max_length=50, blank=True, null=True
    )
    booking_link = models.URLField(null=True, blank=True)
    discover_moscow_link = models.URLField(null=True, blank=True)
    duration = models.IntegerField(blank=True, null=True)
    ticket_price = models.IntegerField(blank=True, null=True)
    schedule = models.JSONField(null=True)


class Hotel(BasePoint):
    address = models.CharField(max_length=250)
    rooms = models.JSONField(null=True)
    email = models.CharField(max_length=250)
    stars = models.IntegerField(null=True)


class HotelPhone(models.Model):
    hotel = models.ForeignKey("Hotel", related_name="phones", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=18)


class Restaurant(BasePoint):
    address = models.CharField(max_length=250)
    bill = models.IntegerField(null=True)
    can_reserve = models.BooleanField(default=True)
    avg_time_visit = models.IntegerField(null=True)
    working_time = models.JSONField(null=True)
    phones = ArrayField(models.CharField(max_length=18), null=True)
