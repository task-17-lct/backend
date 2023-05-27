from celery import shared_task

from passfinder.events.models import City
from passfinder.events.services import get_position_weather

api_url = "https://api.weather.yandex.ru/v2/forecast"


@shared_task
def check_temperature():
    for city in City.objects.all():
        temperature, weather_condition = get_position_weather(city.lat, city.lon)
        city.temperature = temperature
        city.weather_condition = weather_condition
        city.save()
