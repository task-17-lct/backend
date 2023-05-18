from django.db import models
from polymorphic.models import PolymorphicModel


class OIDModel(models.Model):
    oid = models.CharField(primary_key=True, max_length=24)

    class Meta:
        abstract = True


class Region(OIDModel):
    title = models.CharField(max_length=250)


class Country(OIDModel):
    title = models.CharField(max_length=250)


class City(OIDModel):
    title = models.CharField(max_length=250)
    region = models.ForeignKey(
        "Region", related_name="cities", null=True, on_delete=models.SET_NULL
    )


class Tag(OIDModel):
    name = models.CharField(max_length=250)


class BasePoints(OIDModel, PolymorphicModel):
    title = models.CharField(max_length=250)
    description = models.TextField()
    city = models.ForeignKey(
        "City", related_name="places", null=True, on_delete=models.SET_NULL
    )
    region = models.ForeignKey(
        "Region", related_name="points", null=True, on_delete=models.SET_NULL
    )
    creator = models.CharField(max_length=250)
    partner = models.CharField(max_length=250)
    payment_method = models.CharField(max_length=250)
    tags = models.ManyToManyField("Tag", related_name="points")
