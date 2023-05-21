from typing import Any
from rest_framework import viewsets, mixins
from rest_framework.request import Request
from rest_framework.response import Response
from passfinder.events.models import Event
from passfinder.events.api.serializers import EventSerializer
from random import choice
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import TinderProceedSerializer


class TinderView(viewsets.GenericViewSet):
    serializer_class = EventSerializer
    model = Event
    queryset = Event.objects.all()

    @action(methods=['GET'], detail=False, serializer_class=EventSerializer)
    def start(self, request: Request, *args: Any, **kwargs: Any):
        event = EventSerializer(choice(Event.objects.all()))
        return Response(data=event.data, status=200)
    
    @action(methods=['POST'], detail=True, serializer_class=TinderProceedSerializer)
    def proceed(self, request: Request, *args: Any, **kwargs: Any):
        event = EventSerializer(choice(Event.objects.all()))
        return Response(data={'event': event.data}, status=200)
