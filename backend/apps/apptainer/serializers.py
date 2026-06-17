from rest_framework import serializers
from apps.projects.models import Project
from .models import ApptainerDefinition, ApptainerBuildJob
from .validators import validate_build_params, validate_definition_content


class ApptainerDefinitionSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(required=False)
    conversation_id = serializers.IntegerField(read_only=True)
    created_by_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ApptainerDefinition
        fields = "__all__"
        read_only_fields = ["id", "project", "storage_path", "created_by", "created_at", "updated_at"]

    def validate_project_id(self, value):
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("项目不存在")
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get("project_id"):
            raise serializers.ValidationError({"project_id": "请选择项目"})
        return attrs

    def validate_content(self, value):
        errors = validate_definition_content(value)
        if errors:
            raise serializers.ValidationError(errors)
        return value


class ApptainerBuildJobSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(read_only=True)
    definition_id = serializers.IntegerField(read_only=True)
    server_id = serializers.IntegerField(read_only=True)
    created_by_id = serializers.IntegerField(read_only=True)

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

    def validate(self, attrs):
        errors = validate_build_params(attrs["workdir"], attrs["output_name"])
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
