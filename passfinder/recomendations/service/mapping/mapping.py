import pickle

attraction_mapping = None
cinema_mapping = None
plays_mapping = None
excursion_mapping = None
concert_mapping = None

with open('passfinder/recomendations/service/mapping/attractions.pickle', 'rb') as file:
    attraction_mapping = pickle.load(file)


with open('passfinder/recomendations/service/mapping/kino.pickle', 'rb') as file:
    cinema_mapping = pickle.load(file)


with open('passfinder/recomendations/service/mapping/spektakli.pickle', 'rb') as file:
    plays_mapping = pickle.load(file)


with open('passfinder/recomendations/service/mapping/excursii.pickle', 'rb') as file:
    excursion_mapping = pickle.load(file)


with open('passfinder/recomendations/service/mapping/concerts.pickle', 'rb') as file:
    concert_mapping = pickle.load(file)