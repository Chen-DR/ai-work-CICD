from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from apps.common.response import success, error
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, CompleteSerializer
from .services import ChatService


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Conversation.objects.filter(user=self.request.user)
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageListView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation_id=self.kwargs["conversation_pk"]
        ).order_by("created_at")


@api_view(["POST"])
def complete(request):
    ser = CompleteSerializer(data=request.data)
    if not ser.is_valid():
        return error(40001, "Invalid parameters", ser.errors)

    try:
        svc = ChatService()
        result = svc.complete(**ser.validated_data)
        return success(result)
    except Conversation.DoesNotExist:
        return error(40401, "Conversation not found", status=404)
    except Exception as e:
        return error(70001, f"Chat completion failed: {str(e)}", status=500)
