import json
from pprint import pprint

with open("data/regions.json") as f:
    data = json.load(f)


result = []
for r in data:
    reg = {}
    region = r["dictionary_data"]
    reg["id"] = r["_id"]["$oid"]
    if region["city"]:
        reg["city"] = region["city"][0]

    reg["title"] = region["title"]
    reg["url"] = region["url"]
    reg["description"] = region["description"]
    reg["description_title"] = region["description_title"]
    reg["description_short"] = region["short_description"]
    reg["showcase_cards"] = region["showcase_cards"]
    media = []
    for m in region["gallery"]:
        media.append({"file": m["source"]["id"], "type": "image"})

    for m in region["images"]:
        media.append({"file": m["source"]["id"], "type": "image"})

    for m in region["icon"]:
        media.append({"file": m["source"]["id"], "type": "icon"})

    if media:
        reg["media"] = media

    result.append(reg)


def get_regions():
    return result
