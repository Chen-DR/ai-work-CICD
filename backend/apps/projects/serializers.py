from rest_framework import serializers
from .models import Project, ProjectMember


class ProjectSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "owner_id", "created_at", "updated_at"]
        read_only_fields = ["id", "owner_id", "created_at", "updated_at"]


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ["id", "project_id", "user_id", "role", "created_at"]
