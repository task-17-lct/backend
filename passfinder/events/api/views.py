from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
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
)
from passfinder.events.models import (
    BasePoint,
    Region,
    City,
    UserRoute,
    UserRoutePoint,
    UserRouteTransaction,
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
        serializer = RouteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        city_id = data["city"]
        start_date = datetime.strptime(data["date_from"], "%Y-%m-%d")
        end_date = datetime.strptime(data["date_to"], "%Y-%m-%d")

        if city_id:
            region = get_object_or_404(City, oid=city_id)
        else:
            region = choice(
                City.objects.annotate(points_count=Count("points")).filter(
                    title__in=city_in_hotels
                )
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

        print(request.user, region, start_date, end_date)

        tour = generate_tour(request.user, region, start_date, end_date)
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


class SaveRouteSerializer(GenericAPIView):
    serializer_class = InputRouteSerializer

    def post(self, request, *args, **kwargs):
        serializer = InputRouteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        route = UserRoute.objects.create(user=self.request.user)
        for point in data["points"]:
            if point["type"] == "point":
                UserRoutePoint.objects.create(
                    route=route, point=BasePoint.objects.get(oid=point["point"])
                )
            else:
                UserRouteTransaction.objects.create(
                    route=route,
                    point_from=BasePoint.objects.get(oid=point["point_from"]),
                    point_to=BasePoint.objects.get(oid=point["point_to"]),
                )

        return Response(data=data)
