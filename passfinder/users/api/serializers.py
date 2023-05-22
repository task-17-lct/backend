from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from passfinder.events.models import BasePoint
from passfinder.users.clickhouse_models import UserPreferenceClickHouse
from passfinder.users.models import UserPreference

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class UserPreferenceSerializer(serializers.ModelSerializer):
    point = serializers.CharField(max_length=24, min_length=24)

    class Meta:
        model = UserPreference
        fields = ["point", "type"]

    def validate_point(self, val):
        return get_object_or_404(BasePoint, oid=val)

    def create(self, validated_data):
        return UserPreference.objects.create(
            user=self.context["request"].user, **validated_data
        )
