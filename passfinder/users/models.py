from django.contrib.auth.models import AbstractUser
from django.db.models import (
    TextChoices,
    ForeignKey,
    CASCADE,
    DateTimeField,
    CharField,
    Index,
)
from django.utils.timezone import now
from django_clickhouse.models import ClickHouseSyncModel

from passfinder.utils.choices import count_max_length


class User(AbstractUser):
    """
    Default custom user model for Pass Finder.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    first_name = None  # type: ignore
    last_name = None  # type: ignore


class UserPreferenceType(TextChoices):
    like = "like"
    dislike = "dislike"
    favorite = "favorite"
    unfavorite = "unfavorite"
    view = "view"
    ignore = "ignore"


class UserPreference(ClickHouseSyncModel):
    user = ForeignKey("User", related_name="preferences", on_delete=CASCADE)
    point = ForeignKey(
        "events.BasePoint", related_name="user_preferences", on_delete=CASCADE
    )
    type = CharField(
        choices=UserPreferenceType.choices,
        max_length=count_max_length(UserPreferenceType),
    )
    created_at = DateTimeField(default=now, db_index=True)

    class Meta:
        indexes = [Index(fields=["user", "point"])]
