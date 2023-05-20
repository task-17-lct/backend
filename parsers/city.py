import json
from pprint import pprint

from django.contrib.gis.geos import Point

with open("data/cities.json") as f:
    data = json.load(f)


result = []
for r in data:
    d = {}
    info = r["dictionary_data"]
    d["id"] = r["_id"]["$oid"]
    d["title"] = info["title"]
    if "region" in info:
        d["region"] = info["region"]
    if "geo_data" in info and info["geo_data"]["coordinates"]:
        d["location"] = Point(
            info["geo_data"]["coordinates"][0], info["geo_data"]["coordinates"][1]
        )

    result.append(d)


def get_cities():
    return result
