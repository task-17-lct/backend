import json
from pprint import pprint

from django.contrib.gis.geos import Point

from passfinder.events.models import City, Region

with open("data/restaurants.json") as f:
    data = json.load(f)


result = []
for r in data:
    d = {}
    al = True
    info = r["dictionary_data"]
    d["oid"] = r["_id"]["$oid"]
    d["title"] = info["title"]
    if "description" in info:
        d["description"] = info["description"]
    else:
        d["description"] = ""
    d["address"] = info["address"]
    if "bill" in info:
        d["bill"] = int(info["bill"])
    if "parser_source" in info:
        d["parser_source"] = info["parser_source"]
    if "avg_time_visit" in info:
        d["avg_time_visit"] = int(info["avg_time_visit"])
    if "can_reserve" in info:
        d["can_reserve"] = bool(info["can_reserve"])
    if "working_time" in info:
        d["working_time"] = info["working_time"]
    if "phones" in info and info["phones"]:
        d["phones"] = info["phones"]

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

    media = []
    if "images" in info:
        for m in info["images"]:
            media.append({"file": m["source"]["id"], "type": "image"})
    if media:
        d["media"] = media

    if al:
        result.append(d)


def get_restaurant():
    return result
