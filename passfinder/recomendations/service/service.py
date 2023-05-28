from annoy import AnnoyIndex
from .mapping.mapping import *
from .models.models import *
from passfinder.events.models import Event, Region, Hotel, BasePoint, City, Restaurant
from passfinder.events.api.serializers import (
    HotelSerializer,
    EventSerializer,
    RestaurantSerializer,
    ObjectRouteSerializer,
)
from passfinder.recomendations.models import *
from random import choice, sample
from collections import Counter
from passfinder.users.models import User
from collections.abc import Iterable
from django.db.models import Q
from geopy.distance import geodesic as GD
from datetime import timedelta, time, datetime
from gevent.pool import Pool
from python_tsp.exact import solve_tsp_dynamic_programming
import numpy as np


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
        museum, "museum", mus_mapping, rev_mus_mapping, nearest_n, mus_model
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
    if event.type == "museum":
        return nearest_mus(event, nearest_n)
    if event.type == "attraction":
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
        if i % 10 == 0:
            print(i)


def generate_nearest_rest():
    NearestEventToRestaurant.objects.all().delete()
    all_events = list(Event.objects.all())
    for i, rest in enumerate(Restaurant.objects.all()):
        sorted_events = list(
            sorted(all_events.copy(), key=lambda event: dist_func(rest, event))
        )
        nearest = NearestEventToRestaurant.objects.create(restaurant=rest)
        nearest.events.set(sorted_events[0:100])
        if i % 10 == 0:
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
        if i % 10 == 0:
            print(i)


def generate_nearest_restaurants():
    rests = list(Restaurant.objects.all())
    for i, event in enumerate(Event.objects.all()):
        sorted_rests = list(sorted(rests.copy(), key=lambda x: dist_func(x, event)))
        nr = NearestRestaurantToEvent.objects.create(event=event)
        nr.restaurants.set(sorted_rests[0:20])
        nr.save()
        if i % 10 == 0:
            print(i)

    for i, hotel in enumerate(Hotel.objects.all()):
        sorted_rests = list(sorted(rests.copy(), key=lambda x: dist_func(x, hotel)))
        nr = NearestRestaurantToHotel.objects.create(hotel=hotel)
        nr.restaurants.set(sorted_rests[0:20])
        nr.save()
        if i % 10 == 0:
            print(i)


def match_points():
    regions = list(City.objects.all())
    for i, point in enumerate(Event.objects.all()):
        s_regions = list(sorted(regions.copy(), key=lambda x: dist_func(point, x)))
        point.city = s_regions[0]
        point.save()
        if i % 10 == 0:
            print(i)
    for i, point in enumerate(Hotel.objects.all()):
        s_regions = list(sorted(regions.copy(), key=lambda x: dist_func(point, x)))
        point.city = s_regions[0]
        point.save()
        if i % 10 == 0:
            print(i)


def match_restaurants():
    regions = list(City.objects.all())

    for i, point in enumerate(Restaurant.objects.all()):
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
    try:
        target_event_idx = rev_mapping[target_event.oid]
    except:
        return 10
    for fav in favorite_events:
        try:
            dists.append(model.get_distance(rev_mapping[fav.oid], target_event_idx))
        except: pass
    try:
        return sum(dists) / len(dists)
    except ZeroDivisionError:
        return 10


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
    if event.type == "attraction":
        preferred = pref.prefferred_attractions.all()
        return calculate_mean_metric(
            preferred, event, attracion_model, rev_attraction_mapping
        )
    if event.type == "museum":
        preferred = pref.prefferred_museums.all()
        return calculate_mean_metric(preferred, event, mus_model, rev_mus_mapping)
    return 10


def get_exponential_koef(time: timedelta):
    time = time.seconds
    if time < 60 * 10:
        return 2
    if time < 60 * 20:
        return 5
    if time < 60 * 30:
        return 10
    if time < 60 * 40:
        return 20
    return int(1e10)


def get_category_similarity_coef(event, user):
    up, _ = UserPreferences.objects.get_or_create(user=user)
    cat = up.preferred_categories
    if event.type in cat:
        return 0.7
    else:
        return 1.2


def get_nearest_favorite(
    events: Iterable[Event],
    user: User,
    base_event: Event,
    exclude_events: Iterable[Event] = [],
    velocity=3.0,
    top_k=1,
):

    sorted_events = list(
        sorted(
            filter(lambda event: event not in exclude_events, events),
            key=lambda event: calculate_favorite_metric(event, user)
            * get_exponential_koef(time_func(dist_func(event, base_event), velocity))
            * get_category_similarity_coef(event, user),
        )
    )

    if top_k == 1:
        return sorted_events[0]

    return sorted_events[0:top_k]


def filter_hotel(region: Region, user: User, stars: Iterable[int]):
    hotels = Hotel.objects.filter(city=region)
    return choice(hotels)


def time_func(km_distance: float, velocity: float):
    return timedelta(minutes=(km_distance) / (velocity / 60))


def generate_route(point1: BasePoint, point2: BasePoint, velocity):
    distance = dist_func(point1, point2)
    time = time_func(distance, velocity)
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
        "time": timedelta(minutes=90 + choice(range(-10, 90, 10))).seconds,
        "distance": 0,
    }


def generate_restaurant(point: BasePoint):
    rest_data = ObjectRouteSerializer(point).data

    return {
        "type": "point",
        "point": rest_data,
        "point_type": "restaurant",
        "time": timedelta(minutes=90 + choice(range(-10, 90, 10))).seconds,
    }


def generate_multiple_tours(
    user: User, city: City, start_date: datetime.date, end_date: datetime.date
):
    hotels = sample(list(Hotel.objects.filter(city=city)), 5)
    pool = Pool(5)
    return pool.map(
        generate_tour, [(user, start_date, end_date, hotel) for hotel in hotels]
    )


def generate_tour(
    user: User,
    city: City,
    start_date: datetime.date,
    end_date: datetime.date,
    avg_velocity=3.0,
    stars=[],
    hotel_type=["hotel", "hostel", "apartment"],
    where_eat=["restaurant", "bar", "cafe"],
    what_to_see=[
        "attractions",
        "museum",
        "movie",
        "concert",
        "artwork",
        "plays",
        "shop",
        "gallery",
        "theme_park",
        "viewpoint",
        "zoo",
    ],
):
    UserPreferences.objects.get_or_create(user=user)

    hotels_candidates = Hotel.objects.filter(city=city)
    if len(hotels_candidates.filter(stars__in=stars)):
        hotels_candidates = hotels_candidates.filter(stars__in=stars)

    try:
        hotel = choice(list(hotels_candidates))
    except:
        hotel = city
    current_date = start_date
    paths, points, disallowed_rest = [], [], []

    while current_date < end_date:
        local_points, local_paths, local_disallowed_rest = generate_path(
            user,
            points,
            hotel,
            disallowed_rest,
            avg_velocity,
            where_eat=where_eat,
            what_to_see=what_to_see,
        )
        points.extend(local_points)
        paths.append({"date": current_date, "paths": local_paths})
        disallowed_rest = local_disallowed_rest
        current_date += timedelta(days=1)
    return paths, points


def generate_hotel(hotel: Hotel):
    hotel_data = ObjectRouteSerializer(hotel).data
    return {
        "type": "point",
        "point": hotel_data,
        "point_type": "hotel",
        "time": 0,
        "distance": 0,
    }


def nearest_distance_points(point: BasePoint, user: User, velocity: float = 3.0):
    nearest = []
    print(isinstance(point, Event), point)
    if isinstance(point, Event):
        nearest = NearestEvent.objects.get(event=point).nearest.all()
    if isinstance(point, Hotel):
        nearest = NearestHotel.objects.get(hotel=point).nearest_events.all()
    if isinstance(point, Restaurant):
        nearest = NearestEventToRestaurant.objects.get(restaurant=point).events.all()

    top_nearest = get_nearest_favorite(nearest, user, point, [], velocity, top_k=10)
    return top_nearest


def generate_path(
    user: User,
    disallowed_points: Iterable[BasePoint],
    hotel: Hotel,
    disallowed_rests: Iterable[Restaurant],
    avg_velocity: float,
    where_eat=["restaurant", "bar", "cafe"],
    what_to_see=[
        "attractions",
        "museum",
        "movie",
        "concert",
        "artwork",
        "plays",
        "shop",
        "gallery",
        "theme_park",
        "viewpoint",
        "zoo",
    ],
):
    allowed_types = [
        "museum",
        "attraction",
        "artwork",
        "shop",
        "gallery",
        "theme_park",
        "zoo",
        "other",
        "viewpoint",
    ]
    if len(set(allowed_types) & set(what_to_see)) == 0:
        allowed_types = what_to_see
    else:
        allowed_types = list(set(allowed_types) & set(what_to_see))
    print(allowed_types, hotel)
    if isinstance(hotel, City):
        start_points_candidate = Restaurant.objects.filter(city=hotel).filter(
            ~Q(oid__in=disallowed_rests)
        )
    else:
        start_points_candidate = (
            NearestRestaurantToHotel.objects.filter(hotel=hotel)
            .first()
            .restaurants.filter(~Q(oid__in=disallowed_rests))
        )

    if len(start_points_candidate.filter(type__in=where_eat)):
        start_points_candidate = start_points_candidate.filter(type__in=where_eat)

    start_point = start_points_candidate[0]
    disallowed_rests.append(start_point.oid)

    candidates = (
        NearestEventToRestaurant.objects.get(restaurant=start_point)
        .events.all()
        .filter(type__in=allowed_types)
    )

    points = [start_point]

    if isinstance(hotel, Hotel):
        path = [
            generate_hotel(hotel),
            generate_route(start_point, hotel, avg_velocity),
            generate_restaurant(start_point),
        ]
    else:
        path = [generate_restaurant(start_point)]

    start_time = datetime.combine(datetime.now(), time(hour=10))

    how_many_eat = 1

    while start_time.hour < 22 and start_time.day == datetime.now().day:
        if (start_time.hour > 14 and how_many_eat == 1) or (
            start_time.hour > 20 and how_many_eat == 2
        ):
            print(points, start_time)
            try:
                point_candidates = (
                    NearestRestaurantToEvent.objects.filter(event=points[-1])
                    .first()
                    .restaurants.filter(~Q(oid__in=disallowed_rests))
                )
                if len(point_candidates.filter(type__in=where_eat)):
                    point_candidates = point_candidates.filter(type__in=where_eat)
                point = point_candidates[0]

                disallowed_rests.append(point.oid)
                points.append(point)

                candidates = (
                    NearestEventToRestaurant.objects.get(restaurant=point)
                    .events.all()
                    .filter(type__in=allowed_types)
                )
                if len(candidates) < 2:
                    candidates = NearestEventToRestaurant.objects.get(
                        restaurant=point
                    ).events.all()

                path.append(generate_restaurant(points[-1]))
                start_time += timedelta(seconds=path[-1]["time"])
                how_many_eat += 1
                continue
            except:
                return points, path, disallowed_rests

        if start_time.hour > 17:
            allowed_types = [
                "play",
                "concert",
                "movie",
                "shop",
                "gallery",
                "theme_park",
                "viewpoint",
            ]
            if len(set(allowed_types) & set(what_to_see)) == 0:
                allowed_types = what_to_see
            else:
                allowed_types = list(set(allowed_types) & set(what_to_see))

        if candidates is None:
            candidates = NearestEvent.objects.get(event=points[-1]).nearest.filter(
                type__in=allowed_types
            )
            if len(candidates) < 2:
                candidates = NearestEvent.objects.get(event=points[-1]).nearest.all()

        try:
            points.append(
                get_nearest_favorite(
                    candidates, user, points[-1], points + disallowed_points
                )
            )

        except:
            points.append(get_nearest_favorite(candidates, user, points[-1], points))

        transition_route = generate_route(points[-1], points[-2], avg_velocity)

        start_time += timedelta(seconds=transition_route["time"])

        point_route = generate_point(points[-1])
        start_time += timedelta(seconds=point_route["time"])
        path.extend([transition_route, point_route])
        candidates = None

        #  = "Сгенерируй описание туристического маршрута, проходящего через следующие точки:\n"
        
        # prompt += 'Отель: {hotel.name}\n'
        # for i in points:
        #     prompt += f'Название: {i.title}\nОписание: {i.description}\nТип: {i.type}\n\n'
        # print(promptprompt)

    return points, path, disallowed_rests


def calculate_distance(
    sample1: Event, samples: Iterable[Event], model: AnnoyIndex, rev_mapping
):
    metrics = []

    for sample in samples:
        metrics.append(
            model.get_distance(rev_mapping[sample1.oid], rev_mapping[sample.oid])
        )

    return sum(metrics) / len(metrics)


def get_onboarding_attractions():
    sample_attractions = sample(list(Event.objects.filter(type="attraction")), 200)
    first_attraction = choice(sample_attractions)

    attractions = [first_attraction]

    while len(attractions) < 10:
        mx_dist = 0
        mx_attraction = None
        for att in sample_attractions:
            if att in attractions:
                continue
            local_dist = calculate_distance(
                att, attractions, attracion_model, rev_attraction_mapping
            )
            if local_dist > mx_dist:
                mx_dist = local_dist
                mx_attraction = att
        attractions.append(mx_attraction)
    return attractions


def get_onboarding_hotels(stars=Iterable[int]):
    return sample(list(Hotel.objects.filter(stars__in=stars)), 10)


def generate_points_path(user: User, points: Iterable[Event], velocity=3.0):
    if len(points) < 7:
        candidates = NearestEvent.objects.get(event=points[0]).nearest.all()
        points.extend(
            list(
                get_nearest_favorite(
                    candidates, user, points[0], [], velocity, 7 - len(points)
                )
            )
        )

    dist_matrix = [[0 for j in range(len(points))] for i in range(len(points))]
    for i in range(len(dist_matrix)):
        for j in range(len(dist_matrix)):
            dist_matrix[i][j] = time_func(
                dist_func(points[i], points[j]), velocity
            ).seconds
    for i in range(len(dist_matrix)):
        dist_matrix[i][0] = 0
    dist_matrix = np.array(dist_matrix)
    dist_matrix[:, 0] = 0
    perm, dist = solve_tsp_dynamic_programming(dist_matrix)

    perm_pts = [points[i] for i in perm]

    res = [generate_point(perm_pts[0])]
    visited_points = [perm_pts[0]]

    for pt in perm_pts[1:]:
        res.extend(
            [generate_route(visited_points[-1], pt, velocity), generate_point(pt)]
        )
        visited_points.append(pt)

    return res


def flat_list(lst):
    res = []
    for i in lst:
        res.extend(i)
    return res


def range_candidates(candidates, user, favorite_events):
    model_mappings = {
        "attraction": [attracion_model, rev_attraction_mapping],
        "museum": [mus_model, rev_mus_mapping],
        "movie": [cinema_model, rev_cinema_mapping],
        "concert": [concert_model, rev_concert_mapping],
        "plays": [plays_model, rev_plays_mapping],
    }
    try:
        if candidates[0].type in ["attraction", "museum", "movie", "concert", "plays"]:
            candidates = sorted(
                map(
                lambda x: [
                        calculate_mean_metric(
                            favorite_events, x, *model_mappings[x.type]
                        ), x
                    ],
                    candidates
                ),
                key=lambda x: x[0],
            )
            return candidates[0:10]
        return sample(candidates, 10)
    except: return []



candidates_generate_strategy = {
        "plays": [
            lambda pref: flat_list(
                list(
                    map(
                        lambda cand: nearest_plays(cand, 30), pref.preffered_plays.all()
                    )
                ),
            ),
            lambda pref: pref.preffered_plays.all(),
        ],
        "movie": [
            lambda pref: flat_list(
                list(
                    map(
                        lambda cand: nearest_movie(cand, 30),
                        pref.preffered_movies.all(),
                    )
                ),
            ),
            lambda pref: pref.preffered_movies.all(),
        ],
        "concert": [
            lambda pref: flat_list(
                list(
                    map(
                        lambda cand: nearest_concert(cand, 30),
                        pref.preferred_concerts.all(),
                    )
                ),
            ),
            lambda pref: pref.preferred_concerts.all(),
        ],
        "attractions": [
            lambda pref: flat_list(
                list(
                    map(
                        lambda cand: nearest_attraction(cand, 30),
                        pref.prefferred_attractions.all(),
                    )
                ),
            ),
            lambda pref: pref.prefferred_attractions.all(),
        ],
        "museum": [
            lambda pref: flat_list(
                list(
                    map(
                        lambda cand: nearest_mus(cand, 30),
                        pref.prefferred_museums.all(),
                    )
                ),
            ),
            lambda pref: pref.prefferred_museums.all(),
        ],
        "shop": [
            lambda pref: sample(list(Event.objects.filter(type="shop")), 10),
            lambda x: [],
        ],
        "gallery": [
            lambda pref: sample(list(Event.objects.filter(type="gallery")), 10),
            lambda x: [],
        ],
        "theme_park": [
            lambda pref: sample(list(Event.objects.filter(type="theme_park")), 10),
            lambda x: [],
        ],
        "viewpoint": [
            lambda pref: sample(list(Event.objects.filter(type="viewpoint")), 10),
            lambda x: [],
        ],
        "zoo": [
            lambda pref: sample(list(Event.objects.filter(type="zoo")), 10),
            lambda x: [],
        ],
        "artwork": [
            lambda pref: sample(list(Event.objects.filter(type="zoo")), 10),
            lambda x: [],
        ],
    }



def get_personal_recomendations(user):
    up, _ = UserPreferences.objects.get_or_create(user=user)

    res = []
    for category_candidate in up.preferred_categories:
        candidates = candidates_generate_strategy[category_candidate][0](up)
        ranged = range_candidates(
            candidates, user, candidates_generate_strategy[category_candidate][1](up)
        )
        res.append(
            {
                "category": category_candidate,
                "events": list(map(lambda x: ObjectRouteSerializer(x[1]).data, ranged)),
            }
        )
    return res


def get_events(
    user: User,
    allowed_regions: Iterable[City],
    what_to_see: Iterable[str]
):
    up, _ = UserPreferences.objects.get_or_create(user=user)
    events = Event.objects.filter(type__in=what_to_see, city__in=allowed_regions)
    ranged = []
    for category in what_to_see:
        candidates = events.filter(type=category)
        ranged.extend(
            range_candidates(
                candidates,
                user,
                candidates_generate_strategy[category][1](up)
            )
        )
    ranged.sort(key=lambda x: x[0])
    return list(
        map(
            lambda x: ObjectRouteSerializer(x[1]).data, 
            ranged[0:10]
        )
    )


def remap_points(date: datetime.date, region: City, )