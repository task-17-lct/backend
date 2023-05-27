from django.utils.dateparse import parse_datetime
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    get_object_or_404,
    RetrieveAPIView,
)
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Count
from random import choice
from passfinder.recomendations.service.service import generate_tour
from datetime import timedelta, datetime
from .consts import *


from passfinder.events.api.serializers import (
    PointSerializer,
    RouteSerializer,
    RegionSerializer,
    RouteInputSerializer,
    CitySerializer,
    InputRouteSerializer,
    ListUserRouteSerializer,
    UserRouteSerializer,
)
from passfinder.events.models import (
    BasePoint,
    Region,
    City,
    UserRoute,
    UserRoutePoint,
    UserRouteTransaction,
    UserRouteDate,
)


class BuildRouteApiView(GenericAPIView):
    serializer_class = RouteSerializer

    @extend_schema(responses={200: RouteSerializer(many=True)})
    def get(self, request):
        routes = []
        for _ in range(10):
            routes.append(
                {
                    "name": "bebra",
                    "date": None,
                    "description": "bebra bebra bebra",
                    "points": PointSerializer(many=True).to_representation(
                        BasePoint.objects.order_by("?")[:10]
                    ),
                }
            )
        return Response(data=routes)

    @extend_schema(
        request=RouteInputSerializer, responses={200: RouteSerializer(many=True)}
    )
    def post(self, request):
        movement_mapping = {"walk": 3.0, "bike": 15.0, "scooter": 30.0, "auto": 50.0}
        serializer = RouteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        city_id = data["city"]
        try:
            start_date = datetime.strptime(data["date_from"], "%Y-%m-%d")
        except:
            start_date = None

        try:
            end_date = datetime.strptime(data["date_to"], "%Y-%m-%d")
        except:
            end_date = None

        try:
            movement = data["movement"]
        except KeyError:
            movement = "walk"

        hotel_stars = data["stars"]
        if hotel_stars is None:
            hotel_stars = []

        hotel_type = data["where_stay"]
        if hotel_type is None:
            hotel_type = ["hotel"]

        where_eat = data["where_eat"]
        if where_eat is None:
            where_eat = ["restaurant", "bar", "cafe"]

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

        if "hotel" not in hotel_type:
            hotel_stars = []
        res = []

        for _ in range(5):
            if city_id:
                region = get_object_or_404(City, oid=city_id)
            else:
                region = choice(
                    City.objects.annotate(points_count=Count("points"))
                    .filter(title__in=city_in_hotels)
                    .filter(points_count__gt=400)
                )
            if not start_date and end_date:
                tour_length = choice([timedelta(days=i) for i in range(1, 4)])
                start_date = end_date - tour_length
            if not end_date and start_date:
                tour_length = choice([timedelta(days=i) for i in range(1, 4)])
                end_date = end_date + tour_length
            if not end_date and not start_date:
                max_date = datetime.now() + timedelta(days=15)
                start_date = choice([max_date - timedelta(days=i) for i in range(1, 5)])
                tour_length = choice([timedelta(days=i) for i in range(1, 4)])
                end_date = start_date + tour_length

            tour = generate_tour(
                request.user,
                region,
                start_date,
                end_date,
                avg_velocity=movement_mapping[movement],
                stars=hotel_stars,
                hotel_type=hotel_type,
                where_eat=where_eat,
                what_to_see=what_to_see,
            )
            res.append(
                {
                    "city": region.title,
                    "date_from": start_date,
                    "date_to": end_date,
                    "path": tour[0],
                }
            )

        return Response(data=res)


class ListRegionApiView(ListAPIView):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class ListCityApiView(ListAPIView):
    serializer_class = CitySerializer
    queryset = (
        City.objects.annotate(points_count=Count("points"))
        .filter(title__in=city_in_hotels)
        .filter(points_count__gt=200)
        .order_by("title")
    )


class SaveRouteApiView(GenericAPIView):
    serializer_class = InputRouteSerializer

    def post(self, request, *args, **kwargs):
        serializer = InputRouteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        route = UserRoute.objects.create(user=self.request.user)
        for date in data["points"]:
            date_obj = UserRouteDate.objects.create(
                date=parse_datetime(date["date"]).date(), route=route
            )
            for point in date["paths"]:
                if point["type"] == "point":
                    UserRoutePoint.objects.create(
                        date=date_obj,
                        duration=point["time"],
                        point=BasePoint.objects.get(oid=point["point"]["oid"]),
                    )
                else:
                    UserRouteTransaction.objects.create(
                        date=date_obj,
                        duration=point["time"],
                        distance=point["distance"],
                    )

        return Response(data=data)


class ListUserFavoriteRoutes(ListAPIView):
    serializer_class = ListUserRouteSerializer

    def get_queryset(self):
        return UserRoute.objects.filter(user=self.request.user)


class RetrieveRoute(RetrieveAPIView):
    serializer_class = UserRouteSerializer

    def get_object(self):
        route = get_object_or_404(UserRoute, pk=self.kwargs["pk"])
        if route.user != self.request.user:
            raise MethodNotAllowed
        return route
