# Generated by Django 4.2.1 on 2023-05-21 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0015_basepoint_lat_basepoint_lon_city_lat_city_lon_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="basepoint",
            name="location",
        ),
        migrations.RemoveField(
            model_name="city",
            name="location",
        ),
        migrations.RemoveField(
            model_name="place",
            name="location",
        ),
    ]
