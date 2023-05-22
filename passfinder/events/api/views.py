from django_filters import DateFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from passfinder.events.api.serializers import PointSerializer, RouteSerializer
from passfinder.events.models import BasePoint


class BuildRouteApiView(GenericAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DateFilter
    serializer_class = RouteSerializer

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
