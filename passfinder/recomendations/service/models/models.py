from annoy import AnnoyIndex

N_DIMENSIONAL = 768

attracion_model = AnnoyIndex(N_DIMENSIONAL, "angular")
attracion_model.load("passfinder/recomendations/service/models/dost.ann")


cinema_model = AnnoyIndex(N_DIMENSIONAL, "angular")
cinema_model.load("passfinder/recomendations/service/models/kino.ann")


plays_model = AnnoyIndex(N_DIMENSIONAL, "angular")
plays_model.load("passfinder/recomendations/service/models/spektatli.ann")


excursion_model = AnnoyIndex(N_DIMENSIONAL, "angular")
excursion_model.load("passfinder/recomendations/service/models/excursii.ann")


concert_model = AnnoyIndex(N_DIMENSIONAL, "angular")
concert_model.load("passfinder/recomendations/service/models/concerts.ann")


mus_model = AnnoyIndex(N_DIMENSIONAL, "angular")
mus_model.load("passfinder/recomendations/service/models/mus.ann")
