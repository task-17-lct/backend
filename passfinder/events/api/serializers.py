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


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["oid", "title"]


class RegionSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = Region
        fields = ["oid", "title", "description_short", "cities"]


class InputRoutePointSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["point", "transition"])
    time = serializers.IntegerField(min_value=0, required=True)

    # point
    point = serializers.CharField(
        min_length=24, max_length=24, required=False, allow_blank=True, allow_null=True
    )

    # transition
    point_from = serializers.CharField(
        min_length=24, max_length=24, required=False, allow_blank=True, allow_null=True
    )
    point_to = serializers.CharField(
        min_length=24, max_length=24, required=False, allow_blank=True, allow_null=True
    )
    distance = serializers.FloatField(min_value=0, required=False, allow_null=True)

    def validate(self, data):
        if data["type"] == "point":
            if "point" not in data or not data["point"]:
                raise serializers.ValidationError("Point id is required")
            get_object_or_404(BasePoint, oid=data["point"])
        else:
            if "point_to" not in data or not data["point_to"]:
                raise serializers.ValidationError("Point to id is required")
            get_object_or_404(BasePoint, oid=data["point_to"])
            if "point_from" not in data or not data["point_from"]:
                raise serializers.ValidationError("Point from id is required")
            get_object_or_404(BasePoint, oid=data["point_from"])
            if "distance" not in data or not data["distance"]:
                raise serializers.ValidationError("Distance is required")

        return data


class InputRouteSerializer(serializers.Serializer):
    points = serializers.ListSerializer(child=InputRoutePointSerializer())


class ResaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        exclude = ("phones",)


class ObjectRouteSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    title = serializers.CharField()
    description = serializers.CharField()
