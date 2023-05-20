from rest_framework import serializers

from passfinder.events.models import Hotel, HotelPhone, City


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
