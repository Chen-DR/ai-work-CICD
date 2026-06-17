from rest_framework import serializers

from .models import ScriptExecutionTask, ScriptFile, ScriptParamPreset
from .validators import parse_args, validate_run_as, validate_timeout


class ScriptFileSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = ScriptFile
        fields = [
            "id", "project", "name", "file_name", "storage_path",
            "description", "language", "content", "created_by",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "storage_path", "language", "created_by", "created_at", "updated_at"]

    def get_content(self, obj):
        if not self.context.get("include_content"):
            return None
        from .services import ScriptService

        return ScriptService().read_script_content(obj)


class ScriptUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)


class ScriptExecuteSerializer(serializers.Serializer):
    server_id = serializers.IntegerField()
    cwd = serializers.CharField(max_length=512)
    args = serializers.CharField(max_length=1024, required=False, allow_blank=True)
    timeout = serializers.IntegerField(required=False)
    run_as = serializers.CharField(max_length=64, required=False, allow_blank=True)

    def validate_args(self, value):
        try:
            parse_args(value or "")
            return value or ""
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_timeout(self, value):
        try:
            return validate_timeout(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_run_as(self, value):
        try:
            return validate_run_as(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ScriptParamPresetSerializer(serializers.ModelSerializer):
    script_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ScriptParamPreset
        fields = [
            "id", "script_id", "name", "args", "last_used_at",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "script_id", "last_used_at", "created_by", "created_at", "updated_at"]

    def validate_args(self, value):
        try:
            parse_args(value or "")
            return value or ""
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ScriptExecutionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptExecutionTask
        fields = "__all__"
        read_only_fields = [
            "task_id", "status", "celery_task_id", "log_path",
            "exit_code", "process_id", "error_message", "created_by",
            "started_at", "finished_at", "created_at", "updated_at",
        ]
