from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("conversations", views.ConversationViewSet, basename="conversation")

urlpatterns = [
    path("complete/", views.complete, name="chat-complete"),
    path("conversations/<int:conversation_pk>/messages/", views.MessageListView.as_view(), name="conversation-messages"),
    path("", include(router.urls)),
]
