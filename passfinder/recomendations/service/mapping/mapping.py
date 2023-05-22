import pickle

attraction_mapping = None
cinema_mapping = None
plays_mapping = None
excursion_mapping = None
concert_mapping = None


def build_dict(list_mapping):
    mapping = {}
    for idx, elem in enumerate(list_mapping):
        mapping.update({elem: idx})
    return mapping


with open('passfinder/recomendations/service/mapping/attractions.pickle', 'rb') as file:
    attraction_mapping = build_dict(pickle.load(file))


with open('passfinder/recomendations/service/mapping/kino.pickle', 'rb') as file:
    cinema_mapping = build_dict(pickle.load(file))


with open('passfinder/recomendations/service/mapping/spektakli.pickle', 'rb') as file:
    plays_mapping = build_dict(pickle.load(file))


with open('passfinder/recomendations/service/mapping/excursii.pickle', 'rb') as file:
    excursion_mapping = build_dict(pickle.load(file))


with open('passfinder/recomendations/service/mapping/concerts.pickle', 'rb') as file:
    concert_mapping = build_dict(pickle.load(file))