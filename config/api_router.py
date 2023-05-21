from rest_framework.routers import DefaultRouter
from passfinder.recomendations.api.views import TinderView, PersonalRecommendation


router = DefaultRouter()

router.register('tinder', TinderView)
router.register("recommendations", PersonalRecommendation)

app_name = "api"
urlpatterns = router.urls