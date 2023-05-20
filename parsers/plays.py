import json
from pprint import pprint

from django.contrib.gis.geos import Point

from passfinder.events.models import City, Region, Place

with open("data/spektatli.json") as f:
    data = json.load(f)


result = []
for r in data:
    al = True
    d = {}
    d["type"] = "plays"
    info = r["dictionary_data"]
    d["oid"] = r["_id"]["$oid"]
    d["title"] = info["title"]
    d["description"] = info["description"]
    if "parser_source" in info:
        d["parser_source"] = info["parser_source"]
    if "sort" in info:
        d["sort"] = int(info["sort"])
    if "is_can_buy" in info:
        d["can_buy"] = info["is_can_buy"]
    if "priority" in info:
        d["priority"] = int(info["priority"])
    if "duration" in info:
        d["duration"] = int(info["duration"])
    if "ticket_price" in info:
        d["ticket_price"] = int(info["ticket_price"])
    if "schedule" in info:
        d["schedule"] = info["schedule"]

    if "payment_method" in info:
        d["payment_method"] = info["payment_method"]
    elif "purchase_method" in info:
        d["payment_method"] = info["purchase_method"]
    if "age" in info:
        d["age"] = info["age"]
    if "booking_link" in info:
        d["booking_link"] = info["booking_link"]
    if "discover_moscow_link" in info:
        d["discover_moscow_link"] = info["discover_moscow_link"]
    if info["city"]:
        try:
            d["city"] = City.objects.get(oid=info["city"])
        except City.DoesNotExist:
            ...
    if "region" in info:
        try:
            d["region"] = Region.objects.get(oid=info["region"])
        except Region.DoesNotExist:
            ...
    if info["place"]:
        try:
            d["place"] = Place.objects.get(oid=info["place"][0])
        except Place.DoesNotExist:
            ...

    if "geo_data" in info and info["geo_data"]["coordinates"]:
        d["location"] = Point(
            info["geo_data"]["coordinates"][0], info["geo_data"]["coordinates"][1]
        )
    else:
        if "place" in d:
            d["location"] = d["place"].location
        else:
            al = False

    media = []
    for m in info["images"]:
        media.append({"file": m["source"]["id"], "type": "image"})

    for m in info["galereya"]:
        media.append({"file": m["source"]["id"], "type": "image"})

    if media:
        d["media"] = media

    if al:
        result.append(d)
    else:
        pprint(d)


def get_spektatli():
    return result
