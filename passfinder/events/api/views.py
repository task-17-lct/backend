from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

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
        region = data["region"]
        routes = []
        if region:
            region = get_object_or_404(Region, oid=region)
            for _ in range(2):
                routes.append(
                    {
                        "name": "bebra",
                        "date": data["date_from"],
                        "description": "bebra bebra bebra",
                        "points": PointSerializer(many=True).to_representation(
                            region.points.all().order_by("?")[:10]
                        ),
                    }
                )
        else:
            for _ in range(10):
                routes.append(
                    {
                        "name": "bebra",
                        "date": data["date_from"],
                        "description": "bebra bebra bebra",
                        "points": PointSerializer(many=True).to_representation(
                            BasePoint.objects.order_by("?")[:10]
                        ),
                    }
                )
        return Response(data=routes)


class ListRegionApiView(ListAPIView):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class ListCityApiView(ListAPIView):
    serializer_class = CitySerializer
    queryset = City.objects.all().order_by("title")


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
