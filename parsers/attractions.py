import json
from pprint import pprint

from passfinder.events.models import Region, Event

with open("data/pos-attr.json") as f:
    data = json.load(f)


reggg = {
    "г. Санкт-Петербург": "Санкт-Петербург",
    "г. Москва": "Москва",
    "г. Севастополь": "Севастополь",
    "Республика Адыгея (Адыгея)": "Республика Адыгея",
    "Чувашская Республика - Чувашия": "Чувашская Республика",
    "Республика Татарстан (Татарстан)": "Республика Татарстан",
    "Республика Северная Осетия - Алания": "Республика Северная Осетия – Алания",
    "Ханты-Мансийский автономный округ - Югра": "Ханты-Мансийский автономный округ — Югра",
}
rett = []
ret = []
for infff in data:
    info = infff["general"]
    if info["address"] and "mapPosition" in info["address"]:
        r_name = (
            reggg[info["region"]["value"]]
            if info["region"]["value"] in reggg
            else info["region"]["value"]
        )
        res = {
            "title": info["name"],
            "parser_source": "mkrf.ru",
            # "region": Region.objects.get(title=r_name),
            "lat": info["address"]["mapPosition"]["coordinates"][0],
            "lon": info["address"]["mapPosition"]["coordinates"][1],
            "address": info["address"]["fullAddress"],
            "type": "attraction",
            "extra_kwargs": {"objectType": info["objectType"]["value"]},
        }
        if "typologies" in info:
            res["extra_kwargs"]["typologies"] = [x["value"] for x in info["typologies"]]

        if "securityInfo" in info or "borderInfo" in info:
            for ev in Event.objects.filter(
                title=info["name"],
                address=res["address"],
                lat=res["lat"],
                lon=res["lon"],
            ):
                ev.extra_kwargs = res["extra_kwargs"]
                ev.save()

        ret.append(res)


def get_att():
    return ret
