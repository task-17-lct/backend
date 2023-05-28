from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from passfinder.events.models import (
    Hotel,
    HotelPhone,
    City,
    Event,
    BasePoint,
    Region,
    Restaurant,
    UserRoute,
    UserRouteDate,
)


class HotelPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelPhone
        exclude = ("hotel",)


class HotelSerializer(serializers.ModelSerializer):
    phones = HotelPhoneSerializer(many=True)
    source = serializers.CharField(source="parser_source")

    class Meta:
        model = Hotel
        exclude = ("oid", "parser_source")


class MuseumSerializer(serializers.ModelSerializer):
    phones = HotelPhoneSerializer(many=True)

    class Meta:
        model = Hotel
        exclude = ("oid",)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("type", "title", "description", "city", "oid")


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasePoint
        fields = ["oid", "title", "description", "location", "icon"]


class RouteSerializer(serializers.Serializer):
    name = serializers.CharField()
    date = serializers.DateField(allow_null=True)
    description = serializers.CharField()
    points = serializers.ListSerializer(child=PointSerializer())


class RouteInputSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    city = serializers.CharField(
        min_length=24, max_length=24, required=False, allow_blank=True, allow_null=True
    )
    movement = serializers.ChoiceField(
        ["walk", "bike", "scooter", "auto"], required=False, allow_blank=True
    )

    stars = serializers.ListField(
        child=serializers.ChoiceField([1, 2, 3, 4, 5]),
        required=False,
        allow_empty=True,
        allow_null=True,
    )
    what_to_see = serializers.ListField(
        child=serializers.ChoiceField(
            [
                "attractions",
                "museum",
                "movie",
                "concert",
                "artwork",
                "plays",
                "shop",
                "gallery",
                "theme_park",
                "viewpoint",
                "zoo",
            ]
        ),
        required=False,
        allow_empty=True,
        allow_null=True,
    )
    where_stay = serializers.ListField(
        child=serializers.ChoiceField(["hotel", "apartment", "hostel"]),
        required=False,
        allow_empty=True,
        allow_null=True,
    )
    where_eat = serializers.ListField(
        child=serializers.ChoiceField(["restaurant", "bar", "cafe"]),
        required=False,
        allow_empty=True,
        allow_null=True,
    )
    with_kids = serializers.BooleanField(required=False, allow_null=True)
    with_animals = serializers.BooleanField(required=False, allow_null=True)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["oid", "title"]


class RegionSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = Region
        fields = ["oid", "title", "description_short", "cities"]


class InputPointJSONSerializer(serializers.Serializer):
    oid = serializers.CharField(min_length=24, max_length=24)


class InputRoutePointSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["point", "transition"])
    time = serializers.IntegerField(min_value=0, required=True)

    # point
    point = InputPointJSONSerializer(required=False, allow_null=True)
    point_type = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    # transition
    distance = serializers.FloatField(required=False, allow_null=True)

    def validate(self, data):
        if data["type"] == "point":
            if (
                "point" not in data
                or not data["point"]
                or "oid" not in data["point"]
                or not data["point"]["oid"]
            ):
                raise serializers.ValidationError("Point id is required")
            get_object_or_404(BasePoint, oid=data["point"]["oid"])
            if "point_type" not in data or not data["point_type"]:
                raise serializers.ValidationError("Point type is required")
        else:
            if "distance" not in data:
                raise serializers.ValidationError("Distance is required")

        return data


class InputRouteDateSerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    paths = serializers.ListSerializer(child=InputRoutePointSerializer())


class InputRouteSerializer(serializers.Serializer):
    points = serializers.ListSerializer(child=InputRouteDateSerializer())


class ListUserRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoute
        fields = ["id", "name", "description", "created"]


class UserRouteDateSerializer(serializers.ModelSerializer):
    paths = serializers.SerializerMethodField(method_name="get_points")

    @extend_schema_field(InputRoutePointSerializer)
    def get_points(self, obj):
        return [x.get_json() for x in obj.points.all()]

    class Meta:
        model = UserRouteDate
        fields = ["date", "paths"]


class UserRouteSerializer(serializers.ModelSerializer):
    points = UserRouteDateSerializer(many=True, source="dates")

    class Meta:
        model = UserRoute
        fields = ["created", "points"]


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        exclude = ("phones",)


class ObjectRouteSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    title = serializers.CharField()
    description = serializers.CharField()
    oid = serializers.CharField()
