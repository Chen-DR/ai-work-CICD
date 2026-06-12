from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("", views.ArtifactViewSet, basename="artifact")
urlpatterns = router.urls
