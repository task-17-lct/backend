from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "passfinder.events"

    def ready(self):
        import passfinder.events.signals  # noqa
