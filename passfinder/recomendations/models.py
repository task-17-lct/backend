from django.db import models
from passfinder.users.models import User
from passfinder.events.models import Event


class UserPreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    preffered_plays = models.ManyToManyField(Event, related_name='preffered_user_play')
    unpreffered_plays = models.ManyToManyField(Event, related_name='unpreffered_users_play')

    preffered_movies = models.ManyToManyField(Event, related_name='preffered_user_movie')
    unpreffered_movies = models.ManyToManyField(Event, related_name='unpreffered_user_movie')

    preferred_concerts = models.ManyToManyField(Event, related_name='preffered_users_concert')
    unpreferred_concerts = models.ManyToManyField(Event, related_name='unpreffered_users_concert')