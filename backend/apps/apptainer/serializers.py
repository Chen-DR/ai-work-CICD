from rest_framework import serializers
from .models import ApptainerDefinition, ApptainerBuildJob


class ApptainerDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApptainerDefinition
        fields = "__all__"
        read_only_fields = ["id", "storage_path", "created_by", "created_at", "updated_at"]


class ApptainerBuildJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApptainerBuildJob
        fields = "__all__"
        read_only_fields = [
            "id", "status", "celery_task_id", "log_path",
            "remote_output_path", "error_message", "started_at",
            "finished_at", "created_by", "created_at", "updated_at",
        ]


class GenerateDefinitionSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    conversation_id = serializers.IntegerField()
    requirement = serializers.CharField(max_length=5000, required=False, allow_blank=True)
    use_knowledge = serializers.BooleanField(default=True)


class CreateBuildJobSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    definition_id = serializers.IntegerField()
    server_id = serializers.IntegerField()
    workdir = serializers.CharField(max_length=512)
    output_name = serializers.CharField(max_length=256)
