from django.db import models
from passfinder.users.models import User
from passfinder.events.models import Event, Hotel, Restaurant, BasePoint
from passfinder.events.api.serializers import ObjectRouteSerializer
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

    prefered_other = models.ManyToManyField(Event, related_name='other_users')
    prefered_hotels = models.ManyToManyField(Hotel, related_name='hotels_user')
    prefered_restaurants = models.ManyToManyField(Restaurant, related_name='restaurant_user')

    def add_point(self, point: BasePoint):
        print(point, type(point))
        if isinstance(point, Event):
            event = point
            if event.type == 'play':
                self.preferred_concerts.add(event)
            elif event.type == 'movie':
                self.preffered_movies.add(event)
            elif event.type == 'attraction':
                self.prefferred_attractions.add(event)
            elif event.type == 'museum':
                self.prefferred_museums.add(event)
            else:
                self.prefered_other.add(event)
            self.save()
        if isinstance(point, Hotel):
            self.prefered_hotels.add(point)
            self.save()
        if isinstance(point, Restaurant):
            self.prefered_restaurants.add(point)
            self.save()
    

    def get_points(self):
        points = [
            *list(self.preffered_plays.all()),
            *list(self.prefered_hotels.all()),
            *list(self.prefered_restaurants.all()),
            *list(self.preferred_concerts.all()),
            *list(self.preffered_movies.all()),
            *list(self.prefferred_attractions.all()),
            *list(self.prefferred_museums.all()),
            *list(self.prefered_other.all()),
        ]
        return list(
            map(
                lambda x: ObjectRouteSerializer(x).data, 
                points
            )
        )

        

class NearestEvent(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="nearest_model_rel"
    )
    nearest = models.ManyToManyField(Event, related_name="nearest_model_rev_rel")


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
