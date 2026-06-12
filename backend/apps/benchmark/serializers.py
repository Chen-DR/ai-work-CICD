from rest_framework import serializers
from .models import BenchmarkScript, BenchmarkJob
from .validators import validate_benchmark_params


class BenchmarkScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenchmarkScript
        fields = "__all__"
        read_only_fields = ["id", "storage_path", "created_by", "created_at", "updated_at"]


class BenchmarkJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenchmarkJob
        fields = "__all__"
        read_only_fields = [
            "id", "status", "celery_task_id", "log_path",
            "report_path", "remote_report_path", "error_message",
            "started_at", "finished_at", "created_by", "created_at", "updated_at",
        ]


class CreateBenchmarkJobSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    script_id = serializers.IntegerField()
    server_id = serializers.IntegerField()
    workdir = serializers.CharField(max_length=512)
    params = serializers.JSONField()

    def validate_params(self, value):
        errors = validate_benchmark_params(value or {})
        if errors:
            raise serializers.ValidationError(errors)
        return value or {}
