import requests

from django.conf import settings

api_url = "https://api.weather.yandex.ru/v2/forecast"


def get_position_weather(lat: float, lon: float) -> list[(str, str)]:
    url = api_url + f"?lat={lat}&lon={lon}&lang=ru_RU&limit=3&hours=false"
    response = requests.get(
        url=url, headers={"X-Yandex-API-Key": settings.YANDEX_TOKEN}
    )

    if response.status_code == 200:
        data = response.json()
        days = []

        for d in data["forecasts"]:
            days.append((d["date"], d["parts"]["day_short"]["condition"]))
        return days
    return []