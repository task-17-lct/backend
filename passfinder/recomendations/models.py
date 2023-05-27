from django.db import models
from passfinder.users.models import User
from passfinder.events.models import Event, Hotel, Restaurant
from django.contrib.postgres.fields import ArrayField


class UserPreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    preffered_plays = models.ManyToManyField(Event, related_name="preffered_user_play")
    unpreffered_plays = models.ManyToManyField(
        Event, related_name="unpreffered_users_play"
    )

    preffered_movies = models.ManyToManyField(
        Event, related_name="preffered_user_movie"
    )
    unpreffered_movies = models.ManyToManyField(
        Event, related_name="unpreffered_user_movie"
    )

    preferred_concerts = models.ManyToManyField(
        Event, related_name="preffered_users_concert"
    )
    unpreferred_concerts = models.ManyToManyField(
        Event, related_name="unpreffered_users_concert"
    )

    prefferred_attractions = models.ManyToManyField(
        Event, related_name="preffered_users_attractions"
    )
    unprefferred_attractions = models.ManyToManyField(
        Event, related_name="unpreffered_users_attractions"
    )

    prefferred_museums = models.ManyToManyField(
        Event, related_name="preffered_users_museums"
    )
    unprefferred_museums = models.ManyToManyField(
        Event, related_name="unpreffered_users_museums"
    )

    preferred_categories = ArrayField(
        base_field=models.CharField(max_length=100), null=True, blank=True
    )
    preferred_stars = ArrayField(
        base_field=models.IntegerField(), null=True, blank=True
    )


class NearestEvent(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="nearest_model_rel"
    )
    nearest = models.ManyToManyField(Event, related_name="nearest_model_rev_rel")


"""
from passfinder.recomendations.service.service import generate_tour

from passfinder.users.models import User

from passfinder.events.models import City
from datetime import datetime

start_date = datetime(year=2023, month=6, day=10)
end_date = datetime(year=2023, month=6, day=13)

c = City.objects.get(title='Таганрог')

u = User.objects.all()[0]

generate_tour(u, c, start_date, end_date)

"""


class NearestHotel(models.Model):
    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE, related_name="nearest_hotel_rel"
    )
    nearest_events = models.ManyToManyField(Event, related_name="nearest_hotel_rev_rel")


class NearestRestaurantToEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    restaurants = models.ManyToManyField(Restaurant)


class NearestRestaurantToHotel(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    restaurants = models.ManyToManyField(Restaurant)


class NearestEventToRestaurant(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event)
