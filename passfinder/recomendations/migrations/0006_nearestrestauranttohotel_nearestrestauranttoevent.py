# Generated by Django 4.2.1 on 2023-05-24 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0019_category_pointcategory_delete_tag"),
        ("recomendations", "0005_userpreferences_prefferred_attractions_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="NearestRestaurantToHotel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "hotel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="events.hotel"
                    ),
                ),
                ("restaurants", models.ManyToManyField(to="events.restaurant")),
            ],
        ),
        migrations.CreateModel(
            name="NearestRestaurantToEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="events.event"
                    ),
                ),
                ("restaurants", models.ManyToManyField(to="events.restaurant")),
            ],
        ),
    ]
