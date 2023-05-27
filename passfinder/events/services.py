import requests

from django.conf import settings

api_url = "https://api.weather.yandex.ru/v2/forecast"


def get_position_weather(lat: float, lon: float) -> (int, str):
    url = api_url + f"?lat={lat}&lon={lon}&lang=ru_RU&limit=1&hours=false"
    response = requests.get(
        url=url, headers={"X-Yandex-API-Key": settings.YANDEX_TOKEN}
    )
    temp_feels = 20
    weather = "clear"
    if response.status_code == 200:
        data = response.json()
        temp_feels = data["forecasts"][0]["parts"]["day"]["feels_like"]
        weather = data["forecasts"][0]["parts"]["day_short"]["condition"]
    return temp_feels, weather
