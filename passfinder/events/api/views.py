from django_filters import DateFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from passfinder.events.api.serializers import PointSerializer
from passfinder.events.models import BasePoint


class BuildRouteApiView(GenericAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DateFilter
    serializer_class = PointSerializer

    def get(self, request):
        return Response(
            data=PointSerializer(many=True).to_representation(
                BasePoint.objects.order_by("?")[:10]
            )
        )
