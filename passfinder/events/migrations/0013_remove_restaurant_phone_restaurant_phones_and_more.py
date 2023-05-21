# Generated by Django 4.2.1 on 2023-05-21 07:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0012_restaurant_address"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="restaurant",
            name="phone",
        ),
        migrations.AddField(
            model_name="restaurant",
            name="phones",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=18), null=True, size=None
            ),
        ),
        migrations.AlterField(
            model_name="restaurant",
            name="avg_time_visit",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="restaurant",
            name="bill",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="restaurant",
            name="can_reserve",
            field=models.BooleanField(default=True),
        ),
    ]
