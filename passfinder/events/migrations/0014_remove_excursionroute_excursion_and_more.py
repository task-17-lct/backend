# Generated by Django 4.2.1 on 2023-05-21 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0013_remove_restaurant_phone_restaurant_phones_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="excursionroute",
            name="excursion",
        ),
        migrations.RemoveField(
            model_name="excursionroute",
            name="point",
        ),
        migrations.DeleteModel(
            name="Excursion",
        ),
        migrations.DeleteModel(
            name="ExcursionRoute",
        ),
    ]
