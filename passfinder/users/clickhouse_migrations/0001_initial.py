from django_clickhouse import migrations

from passfinder.users.clickhouse_models import UserPreferenceClickHouse


class Migration(migrations.Migration):
    operations = [migrations.CreateTable(UserPreferenceClickHouse)]
