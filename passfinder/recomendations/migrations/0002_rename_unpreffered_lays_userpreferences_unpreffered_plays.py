# Generated by Django 4.2.1 on 2023-05-21 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recomendations", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userpreferences",
            old_name="unpreffered_lays",
            new_name="unpreffered_plays",
        ),
    ]
