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
from passfinder.recomendations.models import UserPreferences
from ..service.service import update_preferences_state, get_next_tinder, get_personal_concerts_recommendation, \
    get_personal_plays_recommendation, get_personal_movies_recommendation
from django.views.decorators.csrf import csrf_exempt



class TinderView(viewsets.GenericViewSet):
    serializer_class = EventSerializer
    model = Event
    queryset = Event.objects.all()

    @action(methods=['GET'], detail=False, serializer_class=EventSerializer)
    def start(self, request: Request, *args: Any, **kwargs: Any):
        UserPreferences.objects.get_or_create(user=request.user)
        event = EventSerializer(choice(Event.objects.all()))
        return Response(data=event.data, status=200)
    
    @csrf_exempt
    @action(methods=['POST'], detail=True, serializer_class=TinderProceedSerializer)
    def proceed(self, request: Request, pk):
        update_preferences_state(request.user, Event.objects.get(oid=pk), request.data['action'])
        event = get_next_tinder(request.user, Event.objects.get(oid=pk), request.data['action'])
        if event is None:
            return Response(data={}, status=404)
        return Response(data={'event': EventSerializer(event).data}, status=200)


class PersonalRecommendation(viewsets.GenericViewSet):
    serializer_class = EventSerializer
    model = Event
    queryset = Event.objects.all()

    @action(methods=['GET'], detail=False)
    def plays(self, request, *args, **kwargs):
        recs = get_personal_plays_recommendation(request.user)
        ans = []
        for rec in recs:
            ans.append(EventSerializer(rec[1]).data)
        return Response(ans, 200)
    

    @action(methods=['GET'], detail=False)
    def concerts(self, request, *args, **kwargs):
        recs = get_personal_concerts_recommendation(request.user)
        ans = []
        for rec in recs:
            ans.append(EventSerializer(rec[1]).data)
        return Response(ans, 200)


    @action(methods=['GET'], detail=False)
    def movies(self, request, *args, **kwargs):
        recs = get_personal_movies_recommendation(request.user)
        ans = []
        for rec in recs:
            ans.append(EventSerializer(rec[1]).data)
        return Response(ans, 200)