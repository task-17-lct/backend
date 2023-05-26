from django.urls import path

from passfinder.events.api.views import (
    BuildRouteApiView,
    ListRegionApiView,
    ListCityApiView,
    SaveRouteApiView,
    ListUserFavoriteRoutes,
    RetrieveRoute,
)

app_name = "events"

urlpatterns = [
    path("route/build", BuildRouteApiView.as_view(), name="build_route"),
    path("route/save", SaveRouteApiView.as_view(), name="save_route"),
    path("route/list", ListUserFavoriteRoutes.as_view(), name="list_routes"),
    path("route/<int:pk>", RetrieveRoute.as_view(), name="get_route"),
    path("data/regions", ListRegionApiView.as_view(), name="regions"),
    path("data/cities", ListCityApiView.as_view(), name="cities"),
]
