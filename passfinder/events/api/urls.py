from django.urls import path

from passfinder.events.api.views import BuildRouteApiView

app_name = "events"

urlpatterns = [
    path("route/build", BuildRouteApiView.as_view(), name="build_route")
]
