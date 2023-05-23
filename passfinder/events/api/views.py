from rest_framework.generics import GenericAPIView, ListAPIView, get_object_or_404
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from passfinder.events.api.serializers import (
    PointSerializer,
    RouteSerializer,
    RegionSerializer,
    RouteInputSerializer,
)
from passfinder.events.models import BasePoint, Region


class BuildRouteApiView(GenericAPIView):
    serializer_class = RouteSerializer

    @extend_schema(responses={200: RouteSerializer(many=True)})
    def get(self, request):
        routes = []
        for _ in range(10):
            routes.append(
                {
                    "name": "bebra",
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
        region = serializer.data["region"]
        routes = []
        if region:
            region = get_object_or_404(Region, oid=region)
            for _ in range(2):
                routes.append(
                    {
                        "name": "bebra",
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
