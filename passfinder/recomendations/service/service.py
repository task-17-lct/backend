from annoy import AnnoyIndex
from .mapping.mapping import *
from .models.models import *
from passfinder.events.models import Event


def get_nearest_(instance_model, model_type, mapping, nearest_n, ml_model):
    how_many = len(Event.objects.filter(type=model_type))

    index = mapping.index(instance_model.oid)
    nearest = ml_model.get_nns_by_item(index, len(mapping))

    res = []
    for i in range(how_many):
        try:
            res.append(Event.objects.get(oid=mapping[nearest[i]]))
        except Event.DoesNotExist: ...
        if len(res) == nearest_n: break
    return res


def nearest_attraction(attraction, nearest_n):
    return get_nearest_(attraction, 'attraction', attraction_mapping, nearest_n, attracion_model)


def nearest_movie(movie, nearest_n):
    return get_nearest_(movie, 'movie', cinema_mapping, nearest_n, cinema_model)


def nearest_plays(play, nearest_n):
    return get_nearest_(play, 'play', plays_mapping, nearest_n, plays_model)


def nearest_excursion(excursion, nearest_n):
    return get_nearest_(excursion, 'excursion', excursion_mapping, nearest_n, excursion_model)


def nearest_concert(concert, nearest_n):
    return get_nearest_(concert, 'concert', concert_mapping, nearest_n, concert_model)
