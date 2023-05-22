import json
from pprint import pprint

with open("data/ext.json", "r", encoding="utf-16") as f:
    data = json.load(f)

with open("data/only_cords.json", "r") as f:
    data2 = json.load(f)

ret = []


for j in range(len(data2)):
    info = data["links"][j]
    pos = data2[j]

    if "cords" in pos:
        p_name = [x for x in info.keys() if "плата" in x.lower() or "цена" in x.lower()]

        res = {
            "sort": j,
            "type": "museum",
            "parser_source": "museum.ru",
            "title": info["name"],
            "lat": pos["cords"][0],
            "lon": pos["cords"][1],
        }
        if p_name and info[p_name[0]] != "См. здесь":
            for n in p_name:
                m = []
                if "руб" in info[n]:
                    ppp = info[n].split()
                    for ind, eee in enumerate(ppp):
                        if "руб" in eee:
                            try:
                                val = int(ppp[ind - 1])
                                m.append(val)
                            except Exception:
                                try:
                                    val = int(ppp[ind + 1])
                                    m.append(val)
                                except Exception:
                                    ...
                    if m:
                        res["ticket_price"] = max(m)
                    break

        if "Режим работы" in info and info["Режим работы"] != "См. здесь":
            res["schedule"] = {"plain": info["Режим работы"]}

        if "Описание" in info:
            res["description"] = info["Описание"]

        ret.append(res)


def get_mus():
    return ret
