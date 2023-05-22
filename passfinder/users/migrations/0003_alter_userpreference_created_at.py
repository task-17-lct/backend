# Generated by Django 4.2.1 on 2023-05-22 14:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_userpreference"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userpreference",
            name="created_at",
            field=models.DateTimeField(
                db_index=True, default=django.utils.timezone.now
            ),
        ),
    ]
