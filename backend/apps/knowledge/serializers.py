from rest_framework import serializers
from .models import KnowledgeDocument, KnowledgeChunk


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeDocument
        fields = "__all__"
        read_only_fields = ["id", "storage_path", "status", "error_message", "created_by", "created_at", "updated_at"]


class KnowledgeChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeChunk
        fields = "__all__"


class KnowledgeSearchSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    query = serializers.CharField(max_length=500)
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)
