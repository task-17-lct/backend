from rest_framework import serializers
from passfinder.events.api.serializers import EventSerializer, HotelSerializer


class TinderProceedSerializer(serializers.Serializer):
    action = serializers.ChoiceField(['left', 'right'], write_only=True)
    event = EventSerializer(read_only=True)


class AddToPreferenceSerializer(serializers.Serializer):
    oid = serializers.CharField(write_only=True)


class EventOnboardingRetrieve(serializers.Serializer):
    events = serializers.ListField(child=EventSerializer(), read_only=True)
    types = serializers.ListField(child=serializers.ChoiceField(['park', 'monument', 'museum', 'unseco']), write_only=True)


class HotelOnboardingRetrieve(serializers.Serializer):
    stars = serializers.ListField(child=serializers.ChoiceField([1, 2, 3, 4, 5]), write_only=True)
    hotels = serializers.ListField(child=HotelSerializer(), read_only=True)


class TinderGetEventFilterSerializer(serializers.Serializer):
    type = serializers.ListField(child=serializers.ChoiceField(['attraction', 'museum', 'movie', 'play', 'concert']))
    event = EventSerializer()