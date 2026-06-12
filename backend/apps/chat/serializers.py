from rest_framework import serializers
from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "project_id", "project", "title", "model_name", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "project", "created_at", "updated_at"]
        extra_kwargs = {"project": {"read_only": True}}

    def create(self, validated_data):
        validated_data["project_id"] = validated_data.pop("project_id")
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "conversation_id", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class CompleteSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    conversation_id = serializers.IntegerField()
    message = serializers.CharField(max_length=10000)
    use_knowledge = serializers.BooleanField(default=True)
