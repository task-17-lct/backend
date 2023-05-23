from annoy import AnnoyIndex
from .mapping.mapping import *
from .models.models import *
from passfinder.events.models import Event, Region, Hotel, BasePoint, City
from passfinder.recomendations.models import UserPreferences, NearestEvent, NearestHotel
from random import choice
from collections import Counter
from passfinder.users.models import User
from collections.abc import Iterable
from django.db.models import Q
from geopy.distance import geodesic as GD
from datetime import timedelta, time, datetime


def get_nearest_(instance_model, model_type, mapping, rev_mapping, nearest_n, ml_model):
    how_many = len(Event.objects.filter(type=model_type))

    index = rev_mapping[instance_model.oid]
    nearest = ml_model.get_nns_by_item(index, len(mapping))

    res = []
    for i in range(how_many):
        try:
            res.append(Event.objects.get(oid=mapping[nearest[i]]))
        except Event.DoesNotExist:
            ...
        if len(res) == nearest_n:
            break
    return res


def nearest_attraction(attraction, nearest_n):
    return get_nearest_(
        attraction,
        "attraction",
        attraction_mapping,
        rev_attraction_mapping,
        nearest_n,
        attracion_model,
    )


def nearest_movie(movie, nearest_n):
    return get_nearest_(
        movie, "movie", cinema_mapping, rev_cinema_mapping, nearest_n, cinema_model
    )


def nearest_plays(play, nearest_n):
    return get_nearest_(
        play, "plays", plays_mapping, rev_plays_mapping, nearest_n, plays_model
    )


def nearest_excursion(excursion, nearest_n):
    return get_nearest_(
        excursion,
        "excursion",
        excursion_mapping,
        rev_excursion_mapping,
        nearest_n,
        excursion_model,
    )


def nearest_concert(concert, nearest_n):
    return get_nearest_(
        concert,
        "concert",
        concert_mapping,
        rev_concert_mapping,
        nearest_n,
        concert_model,
    )


def get_nearest_event(event, nearest_n):
    if event.type == "plays":
        return nearest_plays(event, nearest_n)
    if event.type == "concert":
        return nearest_concert(event, nearest_n)
    if event.type == "movie":
        return nearest_movie(event, nearest_n)


def update_preferences_state(user, event, direction):
    pref = UserPreferences.objects.get(user=user)

    if direction == "left":
        if event.type == "plays":
            pref.unpreffered_plays.add(event)
        if event.type == "movie":
            pref.unpreffered_movies.add(event)
        if event.type == "concert":
            pref.unpreferred_concerts.add(event)
    else:
        if event.type == "plays":
            pref.preffered_plays.add(event)
        if event.type == "movie":
            pref.preffered_movies.add(event)
        if event.type == "concert":
            pref.preferred_concerts.add(event)
    pref.save()


def get_next_tinder(user, prev_event, prev_direction):
    pref = UserPreferences.objects.get(user=user)
    print(prev_event.type, len(pref.preferred_concerts.all()))
    if prev_direction == "left":
        if prev_event.type == "plays" and len(pref.unpreffered_plays.all()) <= 2:
            candidates = nearest_plays(prev_event, 100)
            # print(candidates, type(candidates), len(Event.objects.filter(type='plays')))
            return candidates[-1]
        if prev_event.type == "movie" and len(pref.unpreffered_movies.all()) <= 2:
            candidates = nearest_movie(prev_event, 100)
            return candidates[-1]
        if prev_event.type == "concert" and len(pref.unpreferred_concerts.all()) <= 2:
            candidates = nearest_concert(prev_event, 100)
            return candidates[-1]

    if prev_direction == "right":
        if prev_event.type == "plays" and len(pref.preffered_plays.all()) < 2:
            candidates = nearest_plays(prev_event, 2)
            return candidates[1]
        if prev_event.type == "movie" and len(pref.preffered_movies.all()) < 2:
            candidates = nearest_movie(prev_event, 2)
            return candidates[1]
        if prev_event.type == "concert" and len(pref.preferred_concerts.all()) < 2:
            candidates = nearest_concert(prev_event, 2)
            return candidates[1]

    if prev_event.type == "plays":
        if not len(pref.preffered_movies.all()) and not len(
            pref.unpreffered_movies.all()
        ):
            return choice(Event.objects.filter(type="movie"))
        if not len(pref.preferred_concerts.all()) and not len(
            pref.unpreferred_concerts.all()
        ):
            return choice(Event.objects.filter(type="concert"))

    if prev_event.type == "movie":
        if not len(pref.preffered_plays.all()) and not len(
            pref.unpreffered_plays.all()
        ):
            return choice(Event.objects.filter(type="plays"))
        if not len(pref.preferred_concerts.all()) and not len(
            pref.unpreferred_concerts.all()
        ):
            return choice(Event.objects.filter(type="concert"))

    if prev_event.type == "concert":
        if not len(pref.preffered_plays.all()) and not len(
            pref.unpreffered_plays.all()
        ):
            return choice(Event.objects.filter(type="plays"))
        if not len(pref.preffered_movies.all()) and not len(
            pref.unpreffered_movies.all()
        ):
            return choice(Event.objects.filter(type="movie"))

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
            ranks.update({cand: {"rank": 0, "lst": lst}})

    cnt = Counter(flatten_c_list)

    for candidate, how_many in cnt.most_common(len(flatten_c_list)):
        ranks[candidate]["rank"] = how_many * (
            len(ranks[candidate]["lst"]) - ranks[candidate]["lst"].index(candidate)
        )

    res = []
    for cand in ranks.keys():
        res.append((ranks[cand]["rank"], cand))
    return list(
        filter(
            lambda x: x[1] not in flatten_negatives, sorted(res, key=lambda x: -x[0])
        )
    )


def get_personal_recommendation(prefer, unprefer):
    candidates = []
    negative_candidates = []

    for rec in prefer:
        candidates.append(list(map(lambda x: x.oid, get_nearest_event(rec, 10)[1:])))

    for neg in unprefer:
        negative_candidates.append(
            list(map(lambda x: x.oid, get_nearest_event(neg, 10)[1:]))
        )

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


def dist_func(event1: Event, event2: Event):
    # cords1 = [event1.lat, event1.lon]
    # cords2 = [event2.lat, event2.lon]
    # try:
    #     dist = GD(cords1, cords2).km
    #     return dist
    # except:
    #     return 1000000
    return (event1.lon - event2.lon) ** 2 + (event1.lat - event2.lat) ** 2


def generate_nearest():
    NearestEvent.objects.all().delete()
    all_events = list(Event.objects.all())
    for i, event in enumerate(Event.objects.all()):
        event_all_events = list(
            sorted(all_events.copy(), key=lambda x: dist_func(event, x))
        )
        nearest = NearestEvent.objects.create(event=event)
        nearest.nearest.set(event_all_events[0:100])
        nearest.save()
        if i % 100 == 0:
            print(i)


def generate_hotel_nearest():
    NearestHotel.objects.all().delete()
    all_events = list(Event.objects.all())
    hotels = list(Hotel.objects.all())
    for i, hotel in enumerate(hotels):
        event_all_events = list(
            sorted(all_events.copy(), key=lambda x: dist_func(hotel, x))
        )
        nearest = NearestHotel.objects.create(hotel=hotel)
        nearest.nearest_events.set(event_all_events[0:100])
        if i % 100 == 0:
            print(i)


def match_points():
    regions = list(City.objects.all())
    for i, point in enumerate(Event.objects.all()):
        s_regions = list(sorted(regions.copy(), key=lambda x: dist_func(point, x)))
        point.city = s_regions[0]
        point.save()
        if i % 10 == 0:
            print(i)


def calculate_mean_metric(
    favorite_events: Iterable[Event],
    target_event: Event,
    model: AnnoyIndex,
    rev_mapping,
):
    if not len(favorite_events):
        return 100000

    dists = []
    target_event_idx = rev_mapping[target_event.oid]
    for fav in favorite_events:
        dists.append(model.get_distance(rev_mapping[fav.oid], target_event_idx))
    return sum(dists) / len(dists)


def calculate_favorite_metric(event: Event, user: User):
    pref = UserPreferences.objects.get(user=user)
    if event.type == "plays":
        preferred = pref.preffered_plays.all()
        return calculate_mean_metric(preferred, event, plays_model, rev_plays_mapping)
    if event.type == "concert":
        preferred = pref.preferred_concerts.all()
        return calculate_mean_metric(
            preferred, event, concert_model, rev_concert_mapping
        )
    if event.type == "movie":
        preferred = pref.preffered_movies.all()
        return calculate_mean_metric(preferred, event, cinema_model, rev_cinema_mapping)
    return 1000000


def get_nearest_favorite(
    events: Iterable[Event], user: User, exclude_events: Iterable[Event] = []
):
    first_event = None
    for candidate in events:
        if candidate not in exclude_events:
            first_event = candidate
            break

    result = first_event
    result_min = calculate_favorite_metric(result, user)
    for event in events:
        if event in exclude_events:
            continue
        local_min_metric = calculate_favorite_metric(event, user)
        if local_min_metric < result_min:
            result_min = local_min_metric
            result = event

    return result


def filter_hotel(region: Region, user: User, stars: Iterable[int]):
    hotels = Hotel.objects.filter(region=region)
    return choice(hotels)


def time_func(km_distance: float):
    return timedelta(minutes=(km_distance) / (4.0 / 60))


def generate_route(point1: BasePoint, point2: BasePoint):
    distance = dist_func(point1, point2)
    time = time_func(distance)
    return {
        "type": "transition",
        "from": point1,
        "to": point2,
        "distance": distance,
        "time": time,
    }


def generate_point(point: BasePoint):
    return {
        "type": "point",
        "point": point,
        "point_type": "",
        "time": timedelta(minutes=90 + choice(range(-80, 90, 10))),
    }


def generate_path(region: Region, user: User):
    # region_events = Event.objects.filter(region=region)

    hotel = filter_hotel(region, user, [])

    candidates = NearestHotel.objects.get(hotel=hotel).nearest_events.all()

    start_point = get_nearest_favorite(candidates, user, [])

    candidates = NearestEvent.objects.get(event=start_point).nearest.all()

    points = [start_point]

    path = [generate_point(points[-1])]

    start_time = datetime.combine(datetime.now(), time(hour=10))

    while start_time.hour < 22:
        candidates = NearestEvent.objects.get(event=points[-1]).nearest.all()
        points.append(get_nearest_favorite(candidates, user, points))

        transition_route = generate_route(points[-1], points[-2])
        start_time += transition_route["time"]

        point_route = generate_point(points[-1])
        start_time += point_route["time"]
        path.extend([transition_route, point_route])

    return hotel, points, path
