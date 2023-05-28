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
    weather_condition = models.CharField(default="clear", max_length=250)
    temperature = models.IntegerField(default=20)

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


class Category(OIDModel):
    name = models.CharField(max_length=500, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class PointCategory(models.Model):
    point = models.ForeignKey(
        "BasePoint", related_name="categories", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "Category", related_name="points", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("point", "category")


class BasePoint(OIDModel, PolymorphicModel):
    title = models.CharField(max_length=500)
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
    price = models.IntegerField(null=True)

    @property
    @extend_schema_field(
        field=ListSerializer(child=FloatField(), min_length=2, max_length=2)
    )
    def location(self):
        return [self.lat, self.lon]

    @property
    @extend_schema_field(
        field=ListSerializer(child=FloatField(), min_length=2, max_length=2)
    )
    def location_dec(self):
        return [float(format(self.lat, ".6f")), float(format(self.lon, ".6f"))]

    @property
    @extend_schema_field(field=OpenApiTypes.URI)
    def icon(self):
        if self.media:
            return self.media.last().file.url
        return ""

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
        artwork = "artwork", "произведение искусства"
        shop = "shop", "торговый центр"
        gallery = "gallery", "галерея"
        theme_park = "theme_park", "тематический парк"
        viewpoint = "viewpoint", "обзорная точка"
        zoo = "zoo", "зоопарк"
        other = "other", "другое"

    address = models.CharField(max_length=250, null=True)
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

    extra_kwargs = models.JSONField(null=True)


class Hotel(BasePoint):
    class HotelType(models.TextChoices):
        hotel = "hotel", "отель"
        hostel = "hostel", "хостел"
        guest_house = "guest_house", "гостевой дом"
        motel = "motel", "мотель"
        apartment = "apartment", "квартира"
        chalet = "chalet", "домик"

    type = models.CharField(
        db_index=True,
        default=HotelType.hotel,
        choices=HotelType.choices,
        max_length=count_max_length(HotelType),
    )
    address = models.CharField(max_length=500, null=True, blank=True)
    rooms = models.JSONField(null=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    stars = models.IntegerField(null=True)

    extra_kwargs = models.JSONField(null=True)


class HotelPhone(models.Model):
    hotel = models.ForeignKey("Hotel", related_name="phones", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=18)


class Restaurant(BasePoint):
    class RestaurantType(models.TextChoices):
        restaurant = "restaurant", "ресторан"
        bar = "bar", "бар"
        cafe = "cafe", "кафе"

    type = models.CharField(
        db_index=True,
        default=RestaurantType.restaurant,
        choices=RestaurantType.choices,
        max_length=count_max_length(RestaurantType),
    )
    address = models.CharField(max_length=250, blank=True, null=True)
    bill = models.IntegerField(null=True)
    can_reserve = models.BooleanField(default=True)
    avg_time_visit = models.IntegerField(null=True)
    working_time = models.JSONField(null=True)
    phones = ArrayField(models.CharField(max_length=18), null=True)

    extra_kwargs = models.JSONField(null=True)


class UserRoute(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    user = models.ForeignKey(
        "users.User", related_name="routes", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s route"


class UserRouteDate(models.Model):
    date = models.DateField()
    route = models.ForeignKey(
        "UserRoute", related_name="dates", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("date", "route")


class BaseUserRouteDatePoint(PolymorphicModel):
    date = models.ForeignKey(
        "UserRouteDate", related_name="points", on_delete=models.CASCADE
    )
    duration = models.IntegerField()


class UserRoutePoint(BaseUserRouteDatePoint):
    type = "point"
    point = models.ForeignKey("BasePoint", on_delete=models.CASCADE)
    point_type = models.CharField(max_length=250)

    def get_json(self):
        return {
            "type": "point",
            "point": {
                "lat": self.point.lat,
                "lon": self.point.lon,
                "title": self.point.title,
                "description": self.point.description,
                "oid": self.point.oid,
            },
            "point_type": self.point_type,
            "time": self.duration,
        }


class UserRouteTransaction(BaseUserRouteDatePoint):
    type = "transition"
    distance = models.FloatField()

    def get_json(self):
        return {
            "type": "transition",
            "distance": self.distance,
            "time": self.duration,
        }
