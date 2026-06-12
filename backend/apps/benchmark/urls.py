from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("scripts", views.BenchmarkScriptViewSet, basename="benchmark-script")
router.register("jobs", views.BenchmarkJobViewSet, basename="benchmark-job")
urlpatterns = router.urls
