from django.urls import path

from passfinder.events.api.views import BuildRouteApiView, ListRegionApiView

app_name = "events"

urlpatterns = [
    path("route/build", BuildRouteApiView.as_view(), name="build_route"),
    path("regions", ListRegionApiView.as_view(), name="regions"),
]
