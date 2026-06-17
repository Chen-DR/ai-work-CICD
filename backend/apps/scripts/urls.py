from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("scripts", views.ScriptFileViewSet, basename="script")
router.register("scripts/tasks", views.ScriptExecutionTaskViewSet, basename="script-task")

urlpatterns = [
    path("scripts/tasks/<uuid:task_id>/log/stream/", views.stream_task_logs, name="script-task-log-stream"),
    *router.urls,
]
