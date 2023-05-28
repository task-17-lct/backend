from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.dateparse import parse_date

from passfinder.events.models import City, UserRoute
from passfinder.events.services import get_position_weather

weathers_labels = {
    "drizzle": "морось",
    "light-rain": "небольшой дождь",
    "rain": "дождь",
    "moderate-rain": "дождь",
    "heavy-rain": "сильный дождь",
    "continuous-heavy-rain": "сильный дождь",
    "showers": "ливень",
    "wet-snow": "дождь со снегом",
    "snow-showers": "снегопад",
    "hail": "град",
    "thunderstorm": "гроза",
    "thunderstorm-with-rain": "дождь с грозой",
    "thunderstorm-with-hail": "дождь с грозой",
}


@shared_task
def check_temperature():
    cities_temp = {}

    for route in UserRoute.objects.filter(
        dates__date__gte=now().date(), dates__date__lte=now().date() + timedelta(days=3)
    ):
        points = route.dates.objects.get(date=now().date()).points.all()
        cities = points.values_list("city_id").distinct()
        alerts = []
        for city in cities:
            if city:
                city = City.objects.get(oid=city)
                if city in cities_temp:
                    weather_conditions = cities_temp[city]
                else:
                    weather_conditions = get_position_weather(city.lat, city.lon)
                    weather_conditions = [
                        (parse_date(x[0]), x[1]) for x in weather_conditions
                    ]
                    cities_temp[city] = weather_conditions

                for date, weather in weather_conditions:
                    if weather in weathers_labels:
                        alerts.append(
                            f"В городе {city.title} {date.strftime('%d.%m.%Y')} предстоит {weathers_labels[weather]}"
                        )
        if alerts:
            context = {
                "user": route.user,
                "route": route,
                "alerts": alerts,
                # TODO: change to frontend link
                "link": f"http://127.0.0.1:8000/path/{route.id}/change",
            }

            email_plaintext_message = render_to_string("weather_alert.txt", context)
            send_mail(
                "Предупреждение о погоде",
                email_plaintext_message,
                settings.DEFAULT_FROM_EMAIL,
                [route.user.email],
            )
