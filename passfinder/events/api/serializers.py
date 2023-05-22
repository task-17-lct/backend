from rest_framework import serializers

from passfinder.events.models import Hotel, HotelPhone, City, Event, BasePoint


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
