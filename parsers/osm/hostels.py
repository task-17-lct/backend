import json

with open("data/osm/hostel.json") as f:
    data = json.load(f)


ress = []

for el in data["elements"]:
    if "tags" in el and "name" in el["tags"] and "lat" in el and "lon" in el:
        info = el["tags"]
        if "tourism" in info:
            del info["tourism"]
        res = {
            "title": info["name:ru"] if "name:ru" in info else info["name"],
            "type": "hostel",
            "parser_source": "openstreetmap.org",
            "lat": el["lat"],
            "lon": el["lon"],
            "extra_kwargs": info,
        }
        if "rooms" in info:
            res["rooms"] = {"amount": info["rooms"]}

        if "description" in info:
            res["description"] = info["description"]

        if "email" in info:
            res["email"] = info["email"]

        if "stars" in info:
            res["stars"] = int(float(info["stars"]))
        else:
            res["stars"] = 0
        ress.append(res)


def get_hostels():
    return ress
