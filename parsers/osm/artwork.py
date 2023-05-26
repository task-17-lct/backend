import json

with open("data/osm/artwork.json") as f:
    data = json.load(f)


ress = []

for el in data["elements"]:
    if "tags" in el and "name" in el["tags"] and "lat" in el and "lon" in el:
        info = el["tags"]
        if "tourism" in info:
            del info["tourism"]
        res = {
            "title": info["name:ru"] if "name:ru" in info else info["name"],
            "type": "artwork",
            "parser_source": "openstreetmap.org",
            "lat": el["lat"],
            "lon": el["lon"],
            "extra_kwargs": info,
        }
        if "addr:full" in info:
            res["address"] = info["addr:full"]
        else:
            res = []

        if "description" in info:
            res["description"] = info["description"]

        if "email" in info:
            res["email"] = info["email"]

        ress.append(res)


def get_artwork():
    return ress


print([x for x in ress if "address" in x][:10])
