from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    UserPreferenceSerializer,
)
from ..models import UserPreference
from ...events.api.serializers import PointSerializer
from ...events.models import BasePoint

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RegisterApiView(generics.CreateAPIView):
    """Creates new user and sends verification email"""

    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        operation_id="auth_user_register",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CreateUserPreferenceApiView(generics.CreateAPIView):
    serializer_class = UserPreferenceSerializer


class ListUserFavoritePointsApiView(generics.ListAPIView):
    serializer_class = PointSerializer

    def get_queryset(self):
        return BasePoint.objects.filter(
            user_preferences__user=self.request.user, user_preferences__type="favorite"
        )
