from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("documents", views.KnowledgeDocumentViewSet, basename="knowledge-document")

urlpatterns = [
    path("search/", views.search, name="knowledge-search"),
    path("", include(router.urls)),
]
