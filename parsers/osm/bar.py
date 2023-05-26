import json

with open("data/osm/bars.json") as f:
    data = json.load(f)


ress = []

for el in data["elements"]:
    if "tags" in el and "name" in el["tags"] and "lat" in el and "lon" in el:
        info = el["tags"]
        if "tourism" in info:
            del info["tourism"]
        res = {
            "title": info["name:ru"] if "name:ru" in info else info["name"],
            "type": "bar",
            "parser_source": "openstreetmap.org",
            "lat": el["lat"],
            "lon": el["lon"],
        }
        if "addr:full" in info:
            res["address"] = info["addr:full"]
        else:
            addr_res = ""
            names = [x.split(":")[1] for x in info.keys() if "addr:" in x]

            for nnn in ["postcode", "city", "street", "housenumber"]:
                if nnn in names:
                    val = info["addr:" + nnn]
                    if addr_res:
                        if nnn in ["city", "street"]:
                            addr_res += f", {val}"
                        else:
                            addr_res += f" {val}"
                    else:
                        addr_res = val

            if addr_res:
                res["address"] = addr_res

        if "description" in info:
            res["description"] = info["description"]

        if "opening_hours" in info:
            res["working_time"] = {"opening_hours": info["opening_hours"]}

        if "phone" in info:
            res["phones"] = [info["phone"]]

        res["extra_kwargs"] = info

        ress.append(res)


def get_bar():
    return ress
