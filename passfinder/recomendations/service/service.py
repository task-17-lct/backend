from annoy import AnnoyIndex
from .mapping.mapping import *
from .models.models import *
from passfinder.events.models import Event
from passfinder.recomendations.models import UserPreferences
from random import choice
from collections import Counter


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
    return get_nearest_(play, 'plays', plays_mapping, nearest_n, plays_model)


def nearest_excursion(excursion, nearest_n):
    return get_nearest_(excursion, 'excursion', excursion_mapping, nearest_n, excursion_model)


def nearest_concert(concert, nearest_n):
    return get_nearest_(concert, 'concert', concert_mapping, nearest_n, concert_model)


def get_nearest_event(event, nearest_n):
    if event.type == 'plays':
        return nearest_plays(event, nearest_n)
    if event.type == 'concert':
        return nearest_concert(event, nearest_n)
    if event.type == 'movie':
        return nearest_movie(event, nearest_n)


def update_preferences_state(user, event, direction):
    pref = UserPreferences.objects.get(user=user)
    
    if direction == 'left':
        if event.type == 'plays':
            pref.unpreffered_plays.add(event)
        if event.type == 'movie':
            pref.unpreffered_movies.add(event)
        if event.type == 'concert':
            pref.unpreferred_concerts.add(event)
    else:
        if event.type == 'plays':
            pref.preffered_plays.add(event)
        if event.type == 'movie':
            pref.preffered_movies.add(event)
        if event.type == 'concert':
            pref.preferred_concerts.add(event)
    pref.save()



def get_next_tinder(user, prev_event, prev_direction):
    pref = UserPreferences.objects.get(user=user)
    print(prev_event.type, len(pref.preferred_concerts.all()))
    if prev_direction == 'left':
        if prev_event.type == 'plays' and len(pref.unpreffered_plays.all()) <= 2:
            candidates = nearest_plays(prev_event, 100)
            # print(candidates, type(candidates), len(Event.objects.filter(type='plays')))
            return candidates[-1]
        if prev_event.type == 'movie' and len(pref.unpreffered_movies.all()) <= 2:
            candidates = nearest_movie(prev_event, 100)
            return candidates[-1]
        if prev_event.type == 'concert' and len(pref.unpreferred_concerts.all()) <= 2:
            candidates = nearest_concert(prev_event, 100)
            return candidates[-1]
    
    if prev_direction == 'right':
        if prev_event.type == 'plays' and len(pref.preffered_plays.all()) < 2:
            candidates = nearest_plays(prev_event, 2)
            return candidates[1]
        if prev_event.type == 'movie' and len(pref.preffered_movies.all()) < 2:
            candidates = nearest_movie(prev_event, 2)
            return candidates[1]
        if prev_event.type == 'concert' and len(pref.preferred_concerts.all()) < 2:
            candidates = nearest_concert(prev_event, 2)
            return candidates[1]
    
    if prev_event.type == 'plays':
        if not len(pref.preffered_movies.all()) and not len(pref.unpreffered_movies.all()):
            return choice(Event.objects.filter(type='movie'))
        if not len(pref.preferred_concerts.all()) and not len(pref.unpreferred_concerts.all()):
            return choice(Event.objects.filter(type='concert'))
    
    if prev_event.type == 'movie':
        if not len(pref.preffered_plays.all()) and not len(pref.unpreffered_plays.all()):
            return choice(Event.objects.filter(type='plays'))
        if not len(pref.preferred_concerts.all()) and not len(pref.unpreferred_concerts.all()):
            return choice(Event.objects.filter(type='concert'))
    
    if prev_event.type == 'concert':
        if not len(pref.preffered_plays.all()) and not len(pref.unpreffered_plays.all()):
            return choice(Event.objects.filter(type='plays'))
        if not len(pref.preffered_movies.all()) and not len(pref.unpreffered_movies.all()):
            return choice(Event.objects.filter(type='movie'))

    return None



def rank_candidates(candidates_list, negative_candidates_list):
    flatten_c_list = []
    ranks = {}

    flatten_negatives = []

    for negative in negative_candidates_list:
        flatten_negatives.extend(negative)
    
    for lst in candidates_list:
        flatten_c_list.extend(lst)
        for cand in lst:
            ranks.update({cand: {'rank': 0, 'lst': lst}})
        
    cnt = Counter(flatten_c_list)

    for candidate, how_many in cnt.most_common(len(flatten_c_list)):
        ranks[candidate]['rank'] = how_many * (len(ranks[candidate]['lst']) - ranks[candidate]['lst'].index(candidate))
    
    res = []
    for cand in ranks.keys():
        res.append((ranks[cand]['rank'], cand))
    return list(filter(lambda x: x[1] not in flatten_negatives, sorted(res, key=lambda x: -x[0])))


def get_personal_recommendation(prefer, unprefer):
    candidates = []
    negative_candidates = []

    for rec in prefer:
        candidates.append(list(map(lambda x: x.oid, get_nearest_event(rec, 10)[1:])))
    
    for neg in unprefer:
        negative_candidates.append(list(map(lambda x: x.oid, get_nearest_event(neg, 10)[1:])))
    
    ranked = rank_candidates(candidates, negative_candidates)

    return list(map(lambda x: (x[0], Event.objects.get(oid=x[1])), ranked[0:5]))


def get_personal_plays_recommendation(user):
    pref = UserPreferences.objects.get(user=user)

    prefer = pref.preffered_plays.all()
    unprefer = pref.unpreffered_plays.all()
    return get_personal_recommendation(prefer, unprefer)


def get_personal_concerts_recommendation(user):
    pref = UserPreferences.objects.get(user=user)

    prefer = pref.preferred_concerts.all()
    unprefer = pref.unpreferred_concerts.all()
    return get_personal_recommendation(prefer, unprefer)


def get_personal_movies_recommendation(user):
    pref = UserPreferences.objects.get(user=user)

    prefer = pref.preffered_movies.all()
    unprefer = pref.unpreffered_movies.all()
    return get_personal_recommendation(prefer, unprefer)
