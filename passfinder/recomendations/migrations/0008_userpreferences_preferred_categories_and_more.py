# Generated by Django 4.2.1 on 2023-05-27 10:21

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recomendations", "0007_nearesteventtorestaurant"),
    ]

    operations = [
        migrations.AddField(
            model_name="userpreferences",
            name="preferred_categories",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100),
                blank=True,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="userpreferences",
            name="preferred_stars",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(), blank=True, null=True, size=None
            ),
        ),
    ]