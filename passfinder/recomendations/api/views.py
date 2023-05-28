from typing import Any
from rest_framework import viewsets, mixins
from rest_framework.request import Request
from rest_framework.response import Response
from passfinder.events.models import Event
from passfinder.events.api.serializers import EventSerializer, HotelSerializer
from random import choice
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *
from passfinder.recomendations.models import UserPreferences
from ..service.service import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from random import sample
from passfinder.events.api.serializers import RouteInputSerializer
from passfinder.events.api.consts import city_in_hotels


class TinderView(viewsets.GenericViewSet):
    serializer_class = EventSerializer
    model = Event
    queryset = Event.objects.all()

    @action(methods=["GET"], detail=False, serializer_class=EventSerializer)
    def start(self, request: Request, *args: Any, **kwargs: Any):
        UserPreferences.objects.get_or_create(user=request.user)
        event = EventSerializer(choice(Event.objects.all()))
        return Response(data=event.data, status=200)

    @csrf_exempt
    @action(methods=["POST"], detail=True, serializer_class=TinderProceedSerializer)
    def proceed(self, request: Request, pk):
        update_preferences_state(
            request.user, Event.objects.get(oid=pk), request.data["action"]
        )
        event = get_next_tinder(
            request.user, Event.objects.get(oid=pk), request.data["action"]
        )
        if event is None:
            return Response(data={}, status=404)
        return Response(data={"event": EventSerializer(event).data}, status=200)

    @action(
        methods=["POST"], detail=False, serializer_class=TinderGetEventFilterSerializer
    )
    def get_event(self, request: Request):
        # отдавать под пользователя
        events = Event.objects.filter(type__in=request.data["type"])
        return Response(
            data={"event": EventSerializer(choice(events)).data}, status=200
        )


class PersonalRecommendation(viewsets.GenericViewSet):
    serializer_class = EventSerializer
    model = Event
    queryset = Event.objects.all()

    @action(methods=["GET"], detail=False, serializer_class=SelfRecomendationSerializer)
    def recommendations(self, request, *args, **kwargs):
        return Response(data=get_personal_recomendations(request.user), status=200)

    @action(methods=["GET"], detail=True)
    def get_nearest_user_distance(self, request, pk, *args, **kwargs):
        request_point = pk
        if len(Event.objects.filter(oid=pk)):
            request_point = Event.objects.get(oid=pk)
        elif len(Restaurant.objects.filter(oid=pk)):
            request_point = Restaurant.objects.get(oid=pk)
        else:
            request_point = Hotel.objects.get(oid=pk)
        res = nearest_distance_points(request_point, request.user)
        return Response(
            data=list(map(lambda event: EventSerializer(event).data, res)), status=200
        )

    @action(
        methods=["GET"], detail=False, serializer_class=DailySelectionSerializerInput()
    )
    def get_daily_selection(self, request, *args, **kwargs):
        city = choice(
            City.objects.annotate(points_count=Count("points")).filter(
                points_count__gt=200
            )
        )
        events = sample(list(Event.objects.filter(city=city)), 10)
        return Response(
            data={
                "city": city.title,
                "events": list(map(lambda event: EventSerializer(event).data, events)),
            }
        )

    @action(methods=["POST"], detail=False, serializer_class=DailySelectionSerializer)
    def generate_daily_selection(self, request, *args, **kwargs):
        points = []
        print(request.data['nodes'])
        for point in request.data["nodes"]:
            if point["action"] == "right":
                points.append(Event.objects.get(oid=point["oid"]))

        path = generate_points_path(request.user, points, 3)

        return Response(data={"path": path})
    
    @action(methods=['POST'], detail=False, serializer_class=RouteInputSerializer)
    def build_events(self, request, *args, **kwargs):
        serializer = RouteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data =serializer.data
        
        what_to_see = data["what_to_see"]
        if what_to_see is None:
            what_to_see = [
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
        city_id = data["city"]
        allowed_regions = []
        if city_id:
            allowed_regions = [City.objects.get(oid=city_id)]
        else:
            allowed_regions = sample(
                list(City.objects.annotate(points_count=Count("points"))
                    .filter(title__in=city_in_hotels)
                    .filter(points_count__gt=400)), 5)
        return Response(data=get_events(request.user, allowed_regions, what_to_see))




class OnboardingViewset(viewsets.GenericViewSet):
    serializer_class = EventSerializer
    model = Event
    queryset = Event.objects.all()

    @action(methods=["POST"], detail=False, serializer_class=HotelOnboardingRetrieve)
    def hotels(self, reqeust, *args, **kwargs):
        hotels = get_onboarding_hotels(reqeust.data["stars"])
        res = HotelOnboardingRetrieve({"hotels": hotels}).data

        return Response(res, 200)

    @action(methods=["POST"], detail=False, serializer_class=EventOnboardingRetrieve)
    def event(self, request, *args, **kwargs):
        events = get_onboarding_attractions()
        res = EventOnboardingRetrieve({"events": events}).data

        return Response(res, 200)

    @action(methods=["GET"], detail=True)
    def add_to_favorites(self, request, pk, *args, **kwargs):
        pref, _ = UserPreferences.objects.get_or_create(user=request.user)

        event = Event.objects.get(oid=pk)

        if event.type == "attraction":
            pref.prefferred_attractions.add(event)
        elif event.type == "museum":
            pref.prefferred_museums.add(event)
        elif event.type == "movie":
            pref.preffered_movies.add(event)
        elif event.type == "play":
            pref.preffered_plays.add(event)
        elif event.type == "concert":
            pref.preferred_concerts.add(event)

        pref.save()

        return Response(status=200)

    @action(methods=["POST"], detail=False, serializer_class=StarSelectionSerializer)
    def set_hotel_stars(self, request, *args, **kwargs):
        up, _ = UserPreferences.objects.get_or_create(user=request.user)
        up.preferred_stars = request.data["stars"]
        up.save()
        return Response(status=200)

    @action(
        methods=["POST"], detail=False, serializer_class=CategorySelectionSerializer
    )
    def set_categories(self, request, *args, **kwargs):
        up, _ = UserPreferences.objects.get_or_create(user=request.user)
        up.preferred_categories = request.data["categories"]
        up.save()
        return Response(status=200)
