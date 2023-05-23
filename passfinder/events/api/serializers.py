from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from passfinder.events.models import Hotel, HotelPhone, City, Event, BasePoint, Region


class HotelPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelPhone
        exclude = "hotel"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City


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
        exclude = "oid"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("type", "title", "description", "city", "oid")


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasePoint
        fields = ["title", "description", "location", "icon"]


class RouteSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    points = serializers.ListSerializer(child=PointSerializer())


class RouteInputSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    region = serializers.CharField(
        min_length=24, max_length=24, required=False, allow_blank=True
    )


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["oid", "title", "description_short"]
