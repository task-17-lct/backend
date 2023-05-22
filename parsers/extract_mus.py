import os
import json

import requests

from urllib.parse import urlparse
from bs4 import BeautifulSoup

result = []

url = "http://vrm.museum.ru/mus/list.asp?by=alpha"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
t = soup.find_all("tr")
for j in range(20, len(t)):
    try:
        el = t[j]
        l = str(el.find_all(href=True)[0]).split('"')[1]
        link = "http://vrm.museum.ru" + l
        response = requests.get(link)
        name = BeautifulSoup(
            [x for x in response.text.splitlines() if f"http://www.museum.ru{l}" in x][
                0
            ],
            "html.parser",
        ).text
        soup2 = BeautifulSoup(response.text, "html.parser")
        data2 = []
        for table in soup2.find_all("table"):
            rows = table.find_all("tr")
            data = []
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])
            data2 += data

        data3 = {}
        for row in data2:
            if len(row) > 0:
                rec = []
                for el in row:
                    rec += el.split(":")
                if len(rec) > 1:
                    c_name = " ".join(rec[0].split())
                    desc = " ".join(" ".join(rec[1:]).split())
                    data3[c_name] = desc

        images = []
        img_tags = soup2.find_all("img")
        urls = [img["src"] for img in img_tags]
        add = {
            "name": name,
            "urls": [x for x in urls if "asp" in x],
            "link": link,
        } | data3
        result.append(add)
        print(name)
    except Exception as e:
        print(e)
    print(j, "/", len(t))

    with open("ext.json", "w", encoding="utf-16") as f:
        json.dump({"links": result}, f, ensure_ascii=False, indent=4)

with open("ext.json", "w", encoding="utf-16") as f:
    json.dump({"links": result}, f, ensure_ascii=False, indent=4)
