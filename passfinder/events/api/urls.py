from django.urls import path

from passfinder.events.api.views import (
    BuildRouteApiView,
    ListRegionApiView,
    ListCityApiView,
    SaveRouteSerializer,
)

app_name = "events"

urlpatterns = [
    path("route/build", BuildRouteApiView.as_view(), name="build_route"),
    path("route/save", SaveRouteSerializer.as_view(), name="save_route"),
    path("data/regions", ListRegionApiView.as_view(), name="regions"),
    path("data/cities", ListCityApiView.as_view(), name="cities"),
]
