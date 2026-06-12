from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/projects/", include("apps.projects.urls")),
    path("api/v1/chat/", include("apps.chat.urls")),
    path("api/v1/knowledge/", include("apps.knowledge.urls")),
    path("api/v1/apptainer/", include("apps.apptainer.urls")),
    path("api/v1/benchmark/", include("apps.benchmark.urls")),
    path("api/v1/servers/", include("apps.servers.urls")),
    path("api/v1/artifacts/", include("apps.artifacts.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),
]
