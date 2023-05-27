from rest_framework import serializers
from passfinder.events.api.serializers import (
    EventSerializer,
    HotelSerializer,
    ObjectRouteSerializer,
)


class TinderProceedSerializer(serializers.Serializer):
    action = serializers.ChoiceField(["left", "right"], write_only=True)
    event = EventSerializer(read_only=True)


class AddToPreferenceSerializer(serializers.Serializer):
    oid = serializers.CharField(write_only=True)


class EventOnboardingRetrieve(serializers.Serializer):
    events = serializers.ListField(child=EventSerializer(), read_only=True)
    types = serializers.ListField(
        child=serializers.ChoiceField(["park", "monument", "museum", "unseco"]),
        write_only=True,
    )


class HotelOnboardingRetrieve(serializers.Serializer):
    stars = serializers.ListField(
        child=serializers.ChoiceField([1, 2, 3, 4, 5]), write_only=True
    )
    hotels = serializers.ListField(child=HotelSerializer(), read_only=True)


class TinderGetEventFilterSerializer(serializers.Serializer):
    type = serializers.ListField(
        child=serializers.ChoiceField(
            ["attraction", "museum", "movie", "play", "concert"]
        )
    )
    event = EventSerializer()


class DailySelectionNodeSerializer(serializers.Serializer):
    action = serializers.ChoiceField(["left", "right"])
    oid = serializers.CharField()


class DailySelectionSerializerInput(serializers.Serializer):
    city = serializers.CharField(read_only=True)
    events = serializers.ListField(child=EventSerializer(), read_only=True)


class DailySelectionSerializer(serializers.Serializer):
    nodes = serializers.ListField(child=DailySelectionNodeSerializer(), write_only=True)
    type = serializers.ListField(
        child=serializers.ChoiceField(
            ["attraction", "museum", "movie", "play", "concert"]
        )
    )
    event = EventSerializer()


class StarSelectionSerializer(serializers.Serializer):
    stars = serializers.ListField(child=serializers.IntegerField(), write_only=True)


class CategorySelectionSerializer(serializers.Serializer):
    categories = serializers.ListField(
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
        )
    )


class RecomendationNode(serializers.Serializer):
    category = serializers.CharField()
    events = serializers.ListField(child=ObjectRouteSerializer())


class SelfRecomendationSerializer(serializers.Serializer):
    recomendations = serializers.ListField(child=RecomendationNode(), write_only=True)
