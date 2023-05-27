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
        movement_mapping = {
            'walk': 3.0,
            'bike': 15.0,
            'scooter': 30.0,
            'auto': 50.0
        }
        serializer = RouteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        city_id = data["city"]
        start_date = datetime.strptime(data['date_from'], '%Y-%m-%d')
        end_date = datetime.strptime(data['date_to'], '%Y-%m-%d')
        
        try:
            movement = data['movement']
        except KeyError:
            movement = 'walk'
        region = None
        
        if city_id:
            region = get_object_or_404(City, oid=city_id)
        else:
            region = choice(City.objects.annotate(points_count=Count('points')).filter(title__in=city_in_hotels).filter(points_count__gt=300))
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

        print(request.user, region, start_date, end_date)

        tour = generate_tour(request.user, region, start_date, end_date, movement_mapping[movement])
        print(len(tour[1]))

        return Response(data=tour[0])


class ListRegionApiView(ListAPIView):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class ListCityApiView(ListAPIView):
    serializer_class = CitySerializer
    queryset = (
        City.objects.annotate(points_num=Count("points"))
        .filter(points_num__gte=100)
        .order_by("title")
    )


class SaveRouteApiView(GenericAPIView):
    serializer_class = InputRouteSerializer

    def post(self, request, *args, **kwargs):
        serializer = InputRouteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        route = UserRoute.objects.create(user=self.request.user)
        for date in data["dates"]:
            date_obj = UserRouteDate.objects.create(date=date["date"], route=route)
            for point in date["points"]:
                if point["type"] == "point":
                    UserRoutePoint.objects.create(
                        date=date_obj,
                        duration=point["duration"],
                        point=BasePoint.objects.get(oid=point["point"]),
                    )
                else:
                    UserRouteTransaction.objects.create(
                        date=date_obj,
                        duration=point["duration"],
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
