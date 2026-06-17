from rest_framework import serializers
from .models import Server, ServerCredential, ServerAllowedDir, ServerMetric


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = [
            "id", "project_id", "name", "host", "port", "username",
            "auth_type", "status", "allow_script_root", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class ServerCreateSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    name = serializers.CharField(max_length=128)
    host = serializers.CharField(max_length=128)
    port = serializers.IntegerField(default=22)
    username = serializers.CharField(max_length=128)
    auth_type = serializers.ChoiceField(choices=["password", "ssh_key"])
    password = serializers.CharField(required=False, write_only=True)
    ssh_key = serializers.CharField(required=False, write_only=True)


class ServerAllowedDirSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerAllowedDir
        fields = ["id", "server_id", "path", "purpose", "created_at"]


class ServerMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerMetric
        fields = [
            "id", "server_id", "cpu_percent", "mem_percent",
            "mem_used_gb", "mem_total_gb", "gpu_percent", "gpu_mem_percent",
            "disk_percent", "disk_used_gb", "disk_total_gb", "collected_at",
        ]
        read_only_fields = ["id", "collected_at"]
