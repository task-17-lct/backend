from enum import Enum

from django_clickhouse.clickhouse_models import ClickHouseModel
from django_clickhouse.engines import MergeTree
from infi.clickhouse_orm import fields

from passfinder.users.models import UserPreference, UserPreferenceType

UserPreferenceEnumType = Enum(
    "UserPreferenceEnumType", [c[0] for c in UserPreferenceType.choices]
)


class UserPreferenceClickHouse(ClickHouseModel):
    django_model = UserPreference
    sync_enabled = True

    user_id = fields.Int32Field()
    point_id = fields.StringField()
    type = fields.Enum16Field(UserPreferenceEnumType)
    created_at = fields.DateTimeField()

    engine = MergeTree("created_at", ("type", "point_id", "user_id", "created_at"))
