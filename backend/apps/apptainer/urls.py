from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("definitions", views.ApptainerDefinitionViewSet, basename="apptainer-definition")
router.register("build-jobs", views.ApptainerBuildJobViewSet, basename="apptainer-build-job")

urlpatterns = [
    path("generate/", views.generate, name="apptainer-generate"),
    path("", include(router.urls)),
]
