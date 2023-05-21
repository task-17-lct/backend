from rest_framework.routers import DefaultRouter
from passfinder.recomendations.api.views import TinderView


router = DefaultRouter()

router.register('tinder', TinderView)

app_name = "api"
urlpatterns = router.urls