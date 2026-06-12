from rest_framework import serializers
from apps.servers.models import Server
from apps.apptainer.models import ApptainerBuildJob
from apps.benchmark.models import BenchmarkJob
from apps.artifacts.models import Artifact


class ServerHealthSerializer(serializers.ModelSerializer):
    """Server health status for dashboard."""
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Server
        fields = ["id", "name", "host", "port", "username", "auth_type", "status", "status_display"]


class BuildJobBriefSerializer(serializers.ModelSerializer):
    """Brief build job info for dashboard."""
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    definition_name = serializers.CharField(source="definition.name", read_only=True)

    class Meta:
        model = ApptainerBuildJob
        fields = ["id", "definition_name", "status", "status_display", "error_message", "created_at"]


class BenchmarkJobBriefSerializer(serializers.ModelSerializer):
    """Brief benchmark job info for dashboard."""
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    script_name = serializers.CharField(source="script.name", read_only=True)

    class Meta:
        model = BenchmarkJob
        fields = ["id", "script_name", "status", "status_display", "error_message", "created_at"]


class ArtifactBriefSerializer(serializers.ModelSerializer):
    """Brief artifact info for dashboard."""

    class Meta:
        model = Artifact
        fields = ["id", "file_name", "file_size", "created_at"]
