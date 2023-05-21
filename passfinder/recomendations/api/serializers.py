from rest_framework import serializers
from passfinder.events.api.serializers import EventSerializer


class TinderProceedSerializer(serializers.Serializer):
    action = serializers.ChoiceField(['left', 'right'], write_only=True)
    event = EventSerializer(read_only=True)