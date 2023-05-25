# Generated by Django 4.2.1 on 2023-05-25 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0019_category_pointcategory_delete_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="hotel",
            name="extra_kwargs",
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name="hotel",
            name="type",
            field=models.CharField(
                choices=[
                    ("hotel", "отель"),
                    ("hostel", "хостел"),
                    ("guest_house", "гостевой дом"),
                    ("motel", "мотель"),
                ],
                db_index=True,
                default="hotel",
                max_length=11,
            ),
        ),
        migrations.AlterField(
            model_name="hotel",
            name="address",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="hotel",
            name="email",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
