from annoy import AnnoyIndex
from .mapping.mapping import *
from .models.models import *
from passfinder.events.models import Event, Region, Hotel, BasePoint, City, Restaurant
from passfinder.events.api.serializers import HotelSerializer, EventSerializer, ResaurantSerializer, ObjectRouteSerializer
from passfinder.recomendations.models import *
from random import choice, sample
from collections import Counter
from passfinder.users.models import User
from collections.abc import Iterable
from django.db.models import Q
from geopy.distance import geodesic as GD
from datetime import timedelta, time, datetime
from gevent.pool import Pool


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


def nearest_mus(museum, nearest_n):
    return get_nearest_(
        museum,
        "museum",
        mus_mapping,
        rev_mus_mapping,
        nearest_n,
        mus_model
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
    if event.type == 'museum':
        return nearest_mus(event, nearest_n)
    if event.type == 'attraction':
        return nearest_attraction(event, nearest_n)


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
    cords1 = [event1.lat, event1.lon]
    cords2 = [event2.lat, event2.lon]
    try:
        dist = GD(cords1, cords2).km
        return dist
    except:
        return 1000000
    #return (event1.lon - event2.lon) ** 2 + (event1.lat - event2.lat) ** 2


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


def generate_nearest_restaurants():
    rests = list(Restaurant.objects.all())
    for i, event in enumerate(Event.objects.all()):
        sorted_rests = list(sorted(rests.copy(), key=lambda x: dist_func(x, event)))
        nr = NearestRestaurantToEvent.objects.create(event=event)
        nr.restaurants.set(sorted_rests[0:20])
        nr.save()
        if i % 100 == 0:
            print(i)
    
    for i, hotel in enumerate(Hotel.objects.all()):
        sorted_rests = list(sorted(rests.copy(), key=lambda x: dist_func(x, hotel)))
        nr = NearestRestaurantToHotel.objects.create(hotel=hotel)
        nr.restaurants.set(sorted_rests[0:20])
        nr.save()
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
    if event.type == 'attraction':
        preferred = pref.prefferred_attractions.all()
        return calculate_mean_metric(preferred, event, attracion_model, rev_attraction_mapping)
    if event.type == 'museum':
        preferred = pref.prefferred_museums.all()
        return calculate_mean_metric(preferred, event, mus_model, rev_mus_mapping)
    return 1000000


def get_nearest_favorite(
    events: Iterable[Event], user: User, exclude_events: Iterable[Event] = []
):
    first_event = None
    for candidate in events:
        if candidate not in exclude_events:
            first_event = candidate
            break
    
    if first_event is None:
        result = events[0]
    else:
        result = first_event
    result_min = 1000000
    for event in events:
        if event in exclude_events:
            continue
        local_min_metric = calculate_favorite_metric(event, user)
        if local_min_metric < result_min:
            result_min = local_min_metric
            result = event

    return result


def filter_hotel(region: Region, user: User, stars: Iterable[int]):
    hotels = Hotel.objects.filter(city=region)
    return choice(hotels)


def time_func(km_distance: float):
    return timedelta(minutes=(km_distance) / (4.0 / 60))


def generate_route(point1: BasePoint, point2: BasePoint):
    distance = dist_func(point1, point2)
    time = time_func(distance)
    return {
        "type": "transition",
        "distance": distance,
        "time": time.seconds,
    }


def generate_point(point: BasePoint):
    event_data = ObjectRouteSerializer(point).data
    return {
        "type": "point",
        "point": event_data,
        "point_type": "point",
        "time": timedelta(minutes=90+choice(range(-10, 90, 10))).seconds
    }


def generate_restaurant(point: BasePoint):
    rest_data = ObjectRouteSerializer(point).data
    
    return {
        "type": "point",
        "point": rest_data,
        "point_type": "restaurant",
        "time": timedelta(minutes=90+choice(range(-10, 90, 10))).seconds
    }


def generate_multiple_tours(user: User, city: City, start_date: datetime.date, end_date: datetime.date):
    hotels = sample(list(Hotel.objects.filter(city=city)), 5)
    pool = Pool(5)
    return pool.map(generate_tour, [(user, start_date, end_date, hotel) for hotel in hotels])


def generate_tour(user: User, city: City, start_date: datetime.date, end_date: datetime.date):
    UserPreferences.objects.get_or_create(user=user)
    hotel = choice(list(Hotel.objects.filter(city=city)))
    current_date = start_date
    paths, points = [], []

    while current_date < end_date:
        local_points, local_paths = generate_path(user, points, hotel)
        points.extend(local_points)
        paths.append(
            {
                'date': current_date,
                'paths': local_paths
            }
        )

        current_date += timedelta(days=1)
    
    return paths, points


def generate_hotel(hotel: Hotel):
    hotel_data = ObjectRouteSerializer(hotel).data
    return {
        "type": "point",
        "point": hotel_data,
        "point_type": "hotel",
        "time": timedelta(minutes=90+choice(range(-10, 90, 10))).seconds
    }


def generate_path(user: User, disallowed_points: Iterable[BasePoint], hotel: Hotel):
    # region_events = Event.objects.filter(region=region)

    #candidates = NearestHotel.objects.get(hotel=hotel).nearest_events.all()
    allowed_types = ['museum', 'attraction']

    start_point = NearestRestaurantToHotel.objects.get(hotel=hotel).restaurants.first()

    candidates = list(filter(lambda x: x.type in allowed_types, map(lambda x: x.event, start_point.nearestrestauranttoevent_set.all()[0:100])))
    points = [start_point]
    path = [
        generate_hotel(hotel),
        generate_route(start_point, hotel), 
        generate_restaurant(points[-1])
    ]

    start_time = datetime.combine(datetime.now(), time(hour=10))

    how_many_eat = 1


    while start_time.hour < 22 and start_time.day == datetime.now().day:
        if (start_time.hour > 14 and how_many_eat == 1) or (start_time.hour > 20 and how_many_eat == 2):
            point = NearestRestaurantToEvent.objects.get(event=points[-1]).restaurants.all()[0]
            points.append(point)
            candidates = list(filter(lambda x: x.type in allowed_types, map(lambda x: x.event, point.nearestrestauranttoevent_set.all()[0:100])))
            if not len(candidates):
                candidates = list(map(lambda x: x.event, point.nearestrestauranttoevent_set.all()[0:100]))
            
            path.append(generate_restaurant(points[-1]))
            start_time += timedelta(seconds=path[-1]['time'])
            how_many_eat += 1
            continue

        if start_time.hour > 17:
            allowed_types = ['play', 'concert', 'movie']

        if candidates is None:
            candidates = NearestEvent.objects.get(event=points[-1]).nearest.filter(type__in=allowed_types)
            if not len(candidates):
                candidates = NearestEvent.objects.get(event=points[-1]).nearest.all()

        try:
            points.append(get_nearest_favorite(candidates, user, points + disallowed_points))
            
        except AttributeError:
            points.append(get_nearest_favorite(candidates, user, points))

        transition_route = generate_route(points[-1], points[-2])
        start_time += timedelta(seconds=transition_route["time"])

        point_route = generate_point(points[-1])
        start_time += timedelta(seconds=point_route["time"])
        path.extend([transition_route, point_route])
        candidates = None
    return points, path


def calculate_distance(sample1: Event, samples: Iterable[Event], model: AnnoyIndex, rev_mapping):
    metrics = []

    for sample in samples:
        metrics.append(model.get_distance(rev_mapping[sample1.oid], rev_mapping[sample.oid]))
    
    return sum(metrics) / len(metrics)
    

def get_onboarding_attractions():
    sample_attractions = sample(list(Event.objects.filter(type='attraction')), 200)
    first_attraction = choice(sample_attractions)

    attractions = [first_attraction]

    while len(attractions) < 10:
        mx_dist = 0
        mx_attraction = None
        for att in sample_attractions:
            if att in attractions: continue 
            local_dist = calculate_distance(
                att,
                attractions,
                attracion_model, 
                rev_attraction_mapping
            )
            if local_dist > mx_dist:
                mx_dist = local_dist
                mx_attraction = att
        attractions.append(mx_attraction)
    return attractions


def get_onboarding_hotels(stars=Iterable[int]):
    return sample(list(Hotel.objects.filter(stars__in=stars)), 10)