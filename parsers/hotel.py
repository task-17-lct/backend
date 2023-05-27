import json
from pprint import pprint

from django.contrib.gis.geos import Point

from passfinder.events.models import City, Region

with open("data/hotels.json") as f:
    data = json.load(f)


result = []
for r in data:
    d = {}
    al = True
    info = r["dictionary_data"]
    d["oid"] = r["_id"]["$oid"]
    d["title"] = info["title"]
    d["address"] = info["address"]
    if "stars" in info and info["stars"]:
        d["stars"] = int(info["stars"])

    if "city" in info:
        try:
            d["city"] = City.objects.get(oid=info["city"])
        except City.DoesNotExist:
            ...
    if "region" in info:
        try:
            d["region"] = Region.objects.get(oid=info["region"])
        except Region.DoesNotExist:
            ...
    if "geo_data" in info and info["geo_data"]["coordinates"]:
        d["location"] = Point(
            info["geo_data"]["coordinates"][0], info["geo_data"]["coordinates"][1]
        )
    else:
        al = False
    if "rooms" in info:
        d["rooms"] = info["rooms"]

    phones = []
    if "phones" in info:
        for phone in info["phones"]:
            phones.append(
                {"hotel": d["oid"], "name": phone["name"], "number": phone["number"]}
            )
    if phones:
        d["phones"] = phones

    media = []
    if "images" in info:
        for m in info["images"]:
            media.append({"file": m["source"]["id"], "type": "image"})
    if media:
        d["media"] = media

    if al:
        result.append(d)


def get_hotel():
    return result
