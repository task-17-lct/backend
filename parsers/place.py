import json
from pprint import pprint

from django.contrib.gis.geos import Point

from passfinder.events.models import City, Region

with open("data/places.json") as f:
    data = json.load(f)

result = []
for r in data:
    d = {}
    info = r["dictionary_data"]
    d["oid"] = r["_id"]["$oid"]
    d["title"] = info["title"]
    if "description" in info:
        d["description"] = info["description"]
    if "working_time" in info:
        d["working_time"] = info["working_time"]
    else:
        d["description"] = ""
    if "address" in info:
        d["address"] = info["address"]
    if "parser_source" in info:
        d["parser_source"] = info["parser_source"]
    if info["city"]:
        try:
            d["city"] = City.objects.get(oid=info["city"][0])
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
    if "sites" in info:
        d["sites"] = info["sites"]
    if "phones" in info:
        d["phones"] = info["phones"]

    result.append(d)


def get_places():
    return result
