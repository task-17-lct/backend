import pickle

attraction_mapping = None
cinema_mapping = None
plays_mapping = None
excursion_mapping = None
concert_mapping = None

rev_attraction_mapping = None
rev_cinema_mapping = None
rev_plays_mapping = None
rev_excursion_mapping = None
rev_concert_mapping = None


def build_dict(list_mapping):
    mapping = {}
    for idx, elem in enumerate(list_mapping):
        mapping.update({idx: elem})
    return mapping

def build_rev_dict(list_mapping):
    mapping = {}
    for idx, elem in enumerate(list_mapping):
        mapping.update({elem: idx})
    return mapping


with open('passfinder/recomendations/service/mapping/attractions.pickle', 'rb') as file:
    lst = pickle.load(file)
    attraction_mapping = build_dict(lst)
    rev_attraction_mapping = build_rev_dict(lst)


with open('passfinder/recomendations/service/mapping/kino.pickle', 'rb') as file:
    lst = pickle.load(file)
    cinema_mapping = build_dict(lst)
    rev_cinema_mapping = build_rev_dict(lst)


with open('passfinder/recomendations/service/mapping/spektakli.pickle', 'rb') as file:
    lst = pickle.load(file)
    plays_mapping = build_dict(lst)
    rev_plays_mapping = build_rev_dict(lst)


with open('passfinder/recomendations/service/mapping/excursii.pickle', 'rb') as file:
    lst = pickle.load(file)
    excursion_mapping = build_dict(lst)
    rev_excursion_mapping = build_rev_dict(lst)


with open('passfinder/recomendations/service/mapping/concerts.pickle', 'rb') as file:
    lst = pickle.load(file)
    concert_mapping = build_dict(lst)
    rev_concert_mapping = build_rev_dict(lst)