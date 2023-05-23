from django.urls import path, include
from rest_framework.routers import DefaultRouter
from passfinder.recomendations.api.views import TinderView, PersonalRecommendation
from passfinder.users.api.views import (
    UserViewSet,
    CreateUserPreferenceApiView,
    ListUserFavoritePointsApiView,
)

router = DefaultRouter()

router.register("tinder", TinderView)
router.register("recommendations", PersonalRecommendation)
router.register("user", UserViewSet)

app_name = "api"
urlpatterns = [
    path("", include("passfinder.events.api.urls")),
    path("auth/", include("passfinder.users.api.urls")),
    path("user/preference", CreateUserPreferenceApiView.as_view()),
    path("user/favorite", ListUserFavoritePointsApiView.as_view()),
]
urlpatterns += router.urls
